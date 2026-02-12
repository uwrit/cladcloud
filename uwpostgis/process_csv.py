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
    'user': 'clad_svc',
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
    Worker function using pre-initialized connection.

    Args:
        args: tuple of (index, address)
    Returns:
        dict with index and geocoded results
    """
    idx, address = args
    global worker_connection

    try:
        # for debugging:
        # print(f"Processing [{idx}]: {address}")
        if not address or pandas.isna(address) or str(address).strip() == '':
            return {'index': idx, 'status': 'empty'}

        string_to_geocode = '''
            SELECT
                g.rating
            , ST_AsText(ST_SnapToGrid(g.geomout,0.00001)) As wktlonlat
            , (addy).address As stno
            , (addy).streetname As street
            , (addy).streettypeabbrev As styp
            , (addy).location As city
            , (addy).stateabbrev As st
            , (addy).zip FROM geocode(%s) As g;'''

        # Use parameterized query
        try:
            all_results = pandas.read_sql(string_to_geocode, worker_connection, params=(address,))
        except psycopg.Error:
            try:
                worker_connection.rollback()
            except:
                worker_connection.close()
                worker_connection = psycopg.connect(**DB_CONFIG)
                worker_connection.autocommit = True
            return {'index': idx, 'status': 'db_error'}

        if len(all_results) > 0:
            temp_results = all_results.head(1)
            try:
                wkt = temp_results['wktlonlat'].iloc[0]
                if wkt and isinstance(wkt, str):
                    latlong = wkt.replace('POINT(','').replace(')','').split(" ")

                    return {
                        'index': idx,
                        'rating': temp_results['rating'].iloc[0],
                        'stno': temp_results['stno'].iloc[0],
                        'street': temp_results['street'].iloc[0],
                        'styp': temp_results['styp'].iloc[0],
                        'city': temp_results['city'].iloc[0],
                        'st': temp_results['st'].iloc[0],
                        'zip': temp_results['zip'].iloc[0],
                        'lat': float(latlong[1]) if len(latlong) > 1 else None,
                        'lon': float(latlong[0]) if len(latlong) > 0 else None,
                        'status': 'success'
                    }
            except (KeyError, IndexError, ValueError):
                return {'index': idx, 'status': 'parse_error'}

        return {'index': idx, 'status': 'no_results'}

    except Exception as e:
        # print(f"Error processing [{idx}] {address}: {str(e)}")
        return {'index': idx, 'status': 'error'}


def cleanup_worker():
    """Clean up worker resources."""
    global worker_connection
    if 'worker_connection' in globals():
        worker_connection.close()


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
    progress_style = sys.argv[2] if len(sys.argv) > 2 else 'detailed'
    batch_size = int(sys.argv[3]) if len(sys.argv) > 3 else BATCH_SIZE
    num_workers = int(sys.argv[4]) if len(sys.argv) > 4 else cpu_count()
    if progress_style not in ['minimal', 'simple', 'detailed']:
        print(f"Invalid style '{progress_style}'. Using 'detailed'.")
        progress_style = 'detailed'
    print(f"Using {num_workers} worker processes of {batch_size} batch size with {progress_style} output")

    # Import infile
    print(f"Reading in {import_csv}")
    address_df = pandas.read_csv(import_csv)
    # Prepare output columns
    address_df[['rating', 'stno', 'street', 'styp', 'city', 'st', 'zip', 'lat', 'lon']] = None
    # print(f"Total addresses to process: {len(address_df)}")

    # Prepare work items
    work_items = [(idx, row['address']) for idx, row in address_df.iterrows()]
    stats = {'success': 0, 'failed': 0, 'empty': 0, 'db_error': 0,
             'parse_error': 0, 'no_results': 0}

    # Process in parallel with connection pooling
    start_time = time.time()
    with Pool(
        processes=num_workers,
        initializer=init_worker,
        initargs=(DB_CONFIG,)
    ) as pool:
        # Process in chunks for better progress tracking
        results = []
        if progress_style == 'minimal':
            # Minimal: Just a simple progress bar
            with tqdm(total=len(work_items), ncols=30, desc="Processing", unit="addr") as pbar:
                for result in pool.imap_unordered(geocode_address, work_items, chunksize=batch_size):
                    results.append(result)
                    if result.get('status') == 'success':
                        stats['success'] += 1
                    pbar.update(1)

        elif progress_style == 'simple':
            # Simple: Progress bar with success count
            with tqdm(total=len(work_items), ncols=30, desc="Geocoding", unit="addr",
                      bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as pbar:
                for result in pool.imap_unordered(geocode_address, work_items, chunksize=batch_size):
                    results.append(result)
                    status = result.get('status', 'error')

                    if status == 'success':
                        stats['success'] += 1
                    else:
                        stats['failed'] += 1

                    pbar.set_postfix({'✓': stats['success'], '✗': stats['failed']})
                    pbar.update(1)

        else:  # 'detailed'
            # Detailed: Multiple progress bars with comprehensive stats
            main_pbar = tqdm(total=len(work_items), ncols=30, desc="Overall Progress", position=0, unit="addr",
                           bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
            success_pbar = tqdm(total=len(work_items), ncols=30, desc="✓ Successful    ", position=1,
                              bar_format='{desc}: {n_fmt} ({percentage:3.0f}%)', colour='green')
            failed_pbar = tqdm(total=len(work_items), ncols=30, desc="✗ Failed        ", position=2,
                             bar_format='{desc}: {n_fmt} ({percentage:3.0f}%)', colour='red')
            try:
                for result in pool.imap_unordered(geocode_address, work_items, chunksize=batch_size):
                    results.append(result)
                    status = result.get('status', 'error')

                    # Update statistics
                    if status == 'success':
                        stats['success'] += 1
                        success_pbar.update(1)
                    elif status == 'empty':
                        stats['empty'] += 1
                        failed_pbar.update(1)
                    elif status == 'db_error':
                        stats['db_error'] += 1
                        failed_pbar.update(1)
                    elif status == 'parse_error':
                        stats['parse_error'] += 1
                        failed_pbar.update(1)
                    elif status == 'no_results':
                        stats['no_results'] += 1
                        failed_pbar.update(1)
                    else:
                        stats['failed'] += 1
                        failed_pbar.update(1)

                    # Calculate rate
                    elapsed = time.time() - start_time
                    rate = len(results) / elapsed if elapsed > 0 else 0

                    main_pbar.set_postfix({
                        'rate': f'{rate:.1f}/s',
                        'success_rate': f'{100*stats["success"]/len(results):.1f}%'
                    })
                    main_pbar.update(1)

            finally:
                main_pbar.close()
                success_pbar.close()
                failed_pbar.close()

    # Update dataframe with results
    print("\n\nUpdating dataframe...")
    with tqdm(results, desc="Writing results", ncols=30, unit="row", leave=False) as pbar:
        for result in pbar:
            idx = result['index']
            for key, value in result.items():
                if key not in ('index', 'status') and key in address_df.columns:
                    address_df.at[idx, key] = value
    elapsed = time.time() - start_time

    # Summary
    print(f"\n{'='*70}")
    print(f"GEOCODING COMPLETE")
    print(f"{'='*70}")
    print(f"Total addresses:        {len(address_df):,}")
    print(f"Total time:             {elapsed:.2f}s ({elapsed/60:.1f} min)")
    print(f"Average per address:    {elapsed/len(address_df):.3f}s")
    print(f"Processing rate:        {len(address_df)/elapsed:.2f} addresses/sec")
    print(f"Successfully geocoded:  {stats['success']:,} ({100*stats['success']/len(address_df):.1f}%)")
    if stats['empty'] > 0:
        print(f"  Empty addresses:      {stats['empty']:,}")
    if stats['no_results'] > 0:
        print(f"  No results found:     {stats['no_results']:,}")
    if stats['db_error'] > 0:
        print(f"  Database errors:      {stats['db_error']:,}")
    if stats['parse_error'] > 0:
        print(f"  Parse errors:         {stats['parse_error']:,}")
    if stats['failed'] > 0:
        print(f"  Other errors:         {stats['failed']:,}")
    print(f"{'='*70}\n")

    # Write output
    output_csv = os.path.dirname(os.path.abspath(import_csv)) + "/outfile.csv"
    print(f"Writing to {output_csv}")
    address_df.to_csv(output_csv, index=False)
