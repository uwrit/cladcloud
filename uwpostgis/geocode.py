#!/usr/bin/env python3

import os
import pandas
import psycopg
import subprocess
import sys
import time
import warnings
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
warnings.filterwarnings('ignore')

# database connection configuration
DB_CONFIG = {
    'dbname': 'geocoder',
    'user': 'postgres',
    'password': 'not_on_gitlab',
    'host': 'localhost',
    'port': 5432
}

# default batch size for processing
BATCH_SIZE = 100

def init_worker(db_config):
    """Initialize worker process with database autocommit connection."""
    global worker_connection
    worker_connection = psycopg.connect(**db_config)
    worker_connection.autocommit = True

def geocode_address(args):
    """
    Worker function using a Cursor for maximum efficiency.

    Args:
        args: tuple of (index, address)
    Returns:
        dict with index and geocoded results
    """
    idx, address = args
    global worker_connection

    try:
        if not address or pandas.isna(address) or str(address).strip() == '':
            return {'index': idx, 'status': 'empty'}

        sql_query = '''
            SELECT
                g.rating
                , ST_AsText(ST_SnapToGrid(g.geomout,0.00001)) As wktlonlat
                , (addy).address AS street_num
                , (addy).streetname AS street_name
                , (addy).streettypeabbrev AS street_type
                , (addy).location AS city
                , (addy).stateabbrev AS state
                , (addy).zip
            FROM geocode(%s) AS g
            ORDER BY g.rating DESC
            LIMIT 1;'''

        # Using a Cursor instead of read_sql is ~15x faster for single rows
        with worker_connection.cursor() as cur:
            cur.execute(sql_query, (address,))
            row = cur.fetchone()

            if row:
                # Row is a tuple: (rating, wkt, num, name, type, city, state, zip)
                wkt = row[1]
                if wkt and isinstance(wkt, str):
                    latlong = wkt.replace('POINT(','').replace(')','').split(" ")
                    return {
                        'index': idx,
                        'rating': row[0],
                        'street_num': row[2],
                        'street_name': row[3],
                        'street_type': row[4],
                        'city': row[5],
                        'state': row[6],
                        'zip': row[7],
                        'lat': float(latlong[1]) if len(latlong) > 1 else None,
                        'lon': float(latlong[0]) if len(latlong) > 0 else None,
                        'status': 'success'
                    }
        return {'index': idx, 'status': 'no_results'}

    except Exception:
        return {'index': idx, 'status': 'error'}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: process_csv.py <input_csv> [style] [batch_size] [num_workers]")
        print(f"  style:       Progress style: 'minimal', 'simple', or 'detailed' (default: 'detailed')")
        print(f"  batch_size: Progress update frequency (default: {BATCH_SIZE})")
        print(f"  num_workers: Number of parallel processes (default: {cpu_count()})")
        sys.exit(1)

    print("Starting PostgreSQL...")
    subprocess.Popen("postgres")
    time.sleep(1)

    import_csv = sys.argv[1]
    output_csv = "geocoded_" + os.path.basename(import_csv)
    progress_style = sys.argv[2] if len(sys.argv) > 2 else 'detailed'
    batch_size = int(sys.argv[3]) if len(sys.argv) > 3 else BATCH_SIZE
    num_workers = int(sys.argv[4]) if len(sys.argv) > 4 else cpu_count()

    if progress_style not in ['minimal', 'simple', 'detailed']:
        progress_style = 'detailed'
    print(f"Using {num_workers} workers, streaming {import_csv} in chunks of {batch_size}")

    # Get total rows for the progress bar without loading the file into RAM
    total_rows = sum(1 for _ in open(import_csv)) - 1

    stats = {'success': 0, 'failed': 0, 'empty': 0, 'db_error': 0,
             'parse_error': 0, 'no_results': 0, 'error': 0}

    # Initialize progress bars based on style
    if progress_style == 'minimal':
        main_pbar = tqdm(total=total_rows, ncols=100, desc="Processing", unit="addr")
    elif progress_style == 'simple':
        main_pbar = tqdm(total=total_rows, ncols=100, desc="Geocoding", unit="addr",
                        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
    else:
        main_pbar = tqdm(total=total_rows, ncols=100, desc="Overall Progress", position=0, unit="addr")
        success_pbar = tqdm(total=total_rows, ncols=100, desc="✓ Successful    ", position=1, bar_format='{desc}: {n_fmt}', colour='green')
        failed_pbar = tqdm(total=total_rows, ncols=100, desc="✗ Failed        ", position=2, bar_format='{desc}: {n_fmt}', colour='red')

    start_time = time.time()

    with Pool(processes=num_workers, initializer=init_worker, initargs=(DB_CONFIG,)) as pool:
        # Stream the CSV in chunks to keep RAM usage low
        reader = pandas.read_csv(import_csv, chunksize=batch_size)

        for chunk_df in reader:
            # Create a generator for work items (zero RAM footprint)
            work_items = ((idx, row['address']) for idx, row in chunk_df.iterrows())

            chunk_results_list = []
            for result in pool.imap_unordered(geocode_address, work_items):
                status = result.get('status', 'error')

                # Update statistics and UI
                if status == 'success':
                    stats['success'] += 1
                    if progress_style == 'detailed': success_pbar.update(1)
                else:
                    stats[status] = stats.get(status, 0) + 1
                    stats['failed'] += 1
                    if progress_style == 'detailed': failed_pbar.update(1)

                if progress_style == 'simple':
                    main_pbar.set_postfix({'✓': stats['success'], '✗': stats['failed']})

                main_pbar.update(1)

                # Merge the result with the original row data
                orig_row = chunk_df.loc[result['index']].to_dict()
                orig_row.update(result)
                chunk_results_list.append(orig_row)

            # Append the completed chunk to the output file immediately
            out_df = pandas.DataFrame(chunk_results_list)
            out_df.to_csv(output_csv, mode='a', index=False, header=not os.path.exists(output_csv))

            # Explicitly clear chunk memory
            del chunk_results_list
            del out_df

    # Close progress bars
    main_pbar.close()
    if progress_style == 'detailed':
        success_pbar.close()
        failed_pbar.close()

    elapsed = time.time() - start_time

    # Final Summary Report
    print(f"\n{'='*70}")
    print(f"GEOCODING COMPLETE")
    print(f"{'='*70}")
    print(f"Total addresses:        {total_rows:,}")
    print(f"Total time:             {elapsed:.2f}s ({elapsed/60:.1f} min)")
    print(f"Average per address:    {elapsed/total_rows:.3f}s")
    print(f"Processing rate:        {total_rows/elapsed:.2f} addresses/sec")
    print(f"Successfully geocoded:  {stats['success']:,} ({100*stats['success']/total_rows:.1f}%)")
    if stats['empty'] > 0:
        print(f"  Empty addresses:      {stats['empty']:,}")
    if stats['no_results'] > 0:
        print(f"  No results found:     {stats['no_results']:,}")
    if stats['db_error'] > 0:
        print(f"  Database errors:      {stats['db_error']:,}")
    if stats['parse_error'] > 0:
        print(f"  Parse errors:         {stats['parse_error']:,}")
    if stats['error'] > 0:
        print(f"  Other errors:         {stats['error']:,}")
    print(f"{'='*70}\n")
