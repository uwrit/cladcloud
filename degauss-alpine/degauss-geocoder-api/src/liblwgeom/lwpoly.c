/**********************************************************************
 * $Id: lwpoly.c 3639 2009-02-04 00:28:37Z pramsey $
 *
 * PostGIS - Spatial Types for PostgreSQL
 * http://postgis.refractions.net
 * Copyright 2001-2006 Refractions Research Inc.
 *
 * This is free software; you can redistribute and/or modify it under
 * the terms of the GNU General Public Licence. See the COPYING file.
 * 
 **********************************************************************/

/* basic LWPOLY manipulation */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "liblwgeom.h"


#define CHECK_POLY_RINGS_ZM 1

/* construct a new LWPOLY.  arrays (points/points per ring) will NOT be copied
 * use SRID=-1 for unknown SRID (will have 8bit type's S = 0)
 */
LWPOLY *
lwpoly_construct(int SRID, BOX2DFLOAT4 *bbox, unsigned int nrings, POINTARRAY **points)
{
	LWPOLY *result;
	int hasz, hasm;
#ifdef CHECK_POLY_RINGS_ZM
	char zm;
	unsigned int i;
#endif

	if ( nrings < 1 ) lwerror("lwpoly_construct: need at least 1 ring");

	hasz = TYPE_HASZ(points[0]->dims);
	hasm = TYPE_HASM(points[0]->dims);

#ifdef CHECK_POLY_RINGS_ZM
	zm = TYPE_GETZM(points[0]->dims);
	for (i=1; i<nrings; i++)
	{
		if ( zm != TYPE_GETZM(points[i]->dims) )
			lwerror("lwpoly_construct: mixed dimensioned rings");
	}
#endif

	result = (LWPOLY*) lwalloc(sizeof(LWPOLY));
	result->type = lwgeom_makeType_full(hasz, hasm, (SRID!=-1), POLYGONTYPE,
		0);
	result->SRID = SRID;
	result->nrings = nrings;
	result->rings = points;
	result->bbox = bbox;

	return result;
}


/*
 * given the LWPOLY serialized form (or a pointer into a muli* one)
 * construct a proper LWPOLY.
 * serialized_form should point to the 8bit type format (with type = 3)
 * See serialized form doc
 */
LWPOLY *
lwpoly_deserialize(uchar *serialized_form)
{

	LWPOLY *result;
	uint32 nrings;
	int ndims, hasz, hasm;
	uint32 npoints;
	uchar type;
	uchar *loc;
	int t;

	if (serialized_form == NULL)
	{
		lwerror("lwpoly_deserialize called with NULL arg");
		return NULL;
	}

	result = (LWPOLY*) lwalloc(sizeof(LWPOLY));

	type = serialized_form[0];
	result->type = type;

	ndims = TYPE_NDIMS(type);
	hasz = TYPE_HASZ(type);
	hasm = TYPE_HASM(type);
	loc = serialized_form;

	if ( TYPE_GETTYPE(type) != POLYGONTYPE)
	{
		lwerror("lwpoly_deserialize: attempt to deserialize a poly which is really a %s", lwgeom_typename(type));
		return NULL;
	}


	loc = serialized_form+1;

	if (lwgeom_hasBBOX(type)) {
		LWDEBUG(3, "lwpoly_deserialize: input has bbox");

		result->bbox = lwalloc(sizeof(BOX2DFLOAT4));
		memcpy(result->bbox, loc, sizeof(BOX2DFLOAT4));
		loc += sizeof(BOX2DFLOAT4);
	} else {
		result->bbox = NULL;
	}

	if ( lwgeom_hasSRID(type))
	{
		result->SRID = lw_get_int32(loc);
		loc +=4; /* type + SRID */
	}
	else
	{
		result->SRID = -1;
	}

	nrings = lw_get_uint32(loc);
	result->nrings = nrings;
	loc +=4;
	result->rings = (POINTARRAY**) lwalloc(nrings* sizeof(POINTARRAY*));

	for (t =0;t<nrings;t++)
	{
		/* read in a single ring and make a PA */
		npoints = lw_get_uint32(loc);
		loc +=4;

		result->rings[t] = pointArray_construct(loc, hasz, hasm, npoints);
		loc += sizeof(double)*ndims*npoints;
	}

	return result;
}

/*
 * create the serialized form of the polygon
 * result's first char will be the 8bit type.  See serialized form doc
 * points copied
 */
uchar *
lwpoly_serialize(LWPOLY *poly)
{
	size_t size, retsize;
	uchar *result;

	size = lwpoly_serialize_size(poly);
	result = lwalloc(size);
	lwpoly_serialize_buf(poly, result, &retsize);
	
	if ( retsize != size )
	{
		lwerror("lwpoly_serialize_size returned %d, ..serialize_buf returned %d", size, retsize);
	}

	return result;
}

/*
 * create the serialized form of the polygon writing it into the
 * given buffer, and returning number of bytes written into
 * the given int pointer.
 * result's first char will be the 8bit type.  See serialized form doc
 * points copied
 */
void
lwpoly_serialize_buf(LWPOLY *poly, uchar *buf, size_t *retsize)
{
	size_t size=1;  /* type byte */
	char hasSRID;
	int t;
	uchar *loc;
	int ptsize;

	LWDEBUG(2, "lwpoly_serialize_buf called");

	ptsize = sizeof(double)*TYPE_NDIMS(poly->type);

	hasSRID = (poly->SRID != -1);

	size += 4; /* nrings */
	size += 4*poly->nrings; /* npoints/ring */

	buf[0] = (uchar) lwgeom_makeType_full(
		TYPE_HASZ(poly->type), TYPE_HASM(poly->type),
		hasSRID, POLYGONTYPE, poly->bbox ? 1 : 0);
	loc = buf+1;

	if (poly->bbox)
	{
		memcpy(loc, poly->bbox, sizeof(BOX2DFLOAT4));
		size += sizeof(BOX2DFLOAT4); /* bvol */
		loc += sizeof(BOX2DFLOAT4);
	}

	if (hasSRID)
	{
		memcpy(loc, &poly->SRID, sizeof(int32));
		loc += 4;
		size +=4;  /* 4 byte SRID */
	}

	memcpy(loc, &poly->nrings, sizeof(int32));  /* nrings */
	loc+=4;

	for (t=0;t<poly->nrings;t++)
	{
		POINTARRAY *pa = poly->rings[t];
		size_t pasize;
		uint32 npoints;

		if ( TYPE_GETZM(poly->type) != TYPE_GETZM(pa->dims) )
			lwerror("Dimensions mismatch in lwpoly");

		npoints = pa->npoints;

		memcpy(loc, &npoints, sizeof(uint32)); /* npoints this ring */
		loc+=4;

		pasize = npoints*ptsize;
		size += pasize;

		/* copy points */
		memcpy(loc, getPoint_internal(pa, 0), pasize);
		loc += pasize;

	}

	if (retsize) *retsize = size;
}


/* find bounding box (standard one)  zmin=zmax=0 if 2d (might change to NaN) */
BOX3D *
lwpoly_compute_box3d(LWPOLY *poly)
{
	BOX3D *result;

	/* just need to check outer ring -- interior rings are inside */
	POINTARRAY *pa = poly->rings[0];  
	result  = ptarray_compute_box3d(pa);

	return result;
}

/* find length of this serialized polygon */
size_t
lwgeom_size_poly(const uchar *serialized_poly)
{
	uint32 result = 1; /* char type */
	uint32 nrings;
	int ndims;
	int t;
	uchar type;
	uint32 npoints;
	const uchar *loc;

	if (serialized_poly == NULL)
		return -9999;


	type = (uchar) serialized_poly[0];
	ndims = lwgeom_ndims(type);

	if ( lwgeom_getType(type) != POLYGONTYPE)
		return -9999;


	loc = serialized_poly+1;

	if (lwgeom_hasBBOX(type))
	{
		LWDEBUG(3, "lwgeom_size_poly: has bbox");

		loc += sizeof(BOX2DFLOAT4);
		result +=sizeof(BOX2DFLOAT4);
	}


	if ( lwgeom_hasSRID(type))
	{
		LWDEBUG(3, "lwgeom_size_poly: has srid");

		loc +=4; /* type + SRID */
		result += 4;
	}


	nrings = lw_get_uint32(loc);
	loc +=4;
	result +=4;

        LWDEBUGF(3, "lwgeom_size_poly contains %d rings", nrings);

	for (t =0;t<nrings;t++)
	{
		/* read in a single ring and make a PA */
		npoints = lw_get_uint32(loc);
		loc += 4;
		result += 4;

		if (ndims == 3)
		{
			loc += 24*npoints;
			result += 24*npoints;
		}
		else if (ndims == 2)
		{
			loc += 16*npoints;
			result += 16*npoints;
		}
		else if (ndims == 4)
		{
			loc += 32*npoints;
			result += 32*npoints;
		}
	}

        LWDEBUGF(3, "lwgeom_size_poly returning %d", result);

	return result;
}

/* find length of this deserialized polygon */
size_t
lwpoly_serialize_size(LWPOLY *poly)
{
	size_t size = 1; /* type */
	uint32 i;

	if ( poly->SRID != -1 ) size += 4; /* SRID */
	if ( poly->bbox ) size += sizeof(BOX2DFLOAT4);

	LWDEBUGF(2, "lwpoly_serialize_size called with poly[%p] (%d rings)",
			poly, poly->nrings);

	size += 4; /* nrings */

	for (i=0; i<poly->nrings; i++)
	{
		size += 4; /* npoints */
		size += poly->rings[i]->npoints*TYPE_NDIMS(poly->type)*sizeof(double);
	}

	LWDEBUGF(3, "lwpoly_serialize_size returning %d", size);

	return size;
}

void lwpoly_free  (LWPOLY  *poly)
{
	int t;

	if ( poly->bbox )
		lwfree(poly->bbox);

	for (t=0;t<poly->nrings;t++)
	{
		if( poly->rings[t] )
			ptarray_free(poly->rings[t]);
	}

	if ( poly->rings ) 
		lwfree(poly->rings);

	lwfree(poly);
}

void printLWPOLY(LWPOLY *poly)
{
	int t;
	lwnotice("LWPOLY {");
	lwnotice("    ndims = %i", (int)TYPE_NDIMS(poly->type));
	lwnotice("    SRID = %i", (int)poly->SRID);
	lwnotice("    nrings = %i", (int)poly->nrings);
	for (t=0;t<poly->nrings;t++)
	{
		lwnotice("    RING # %i :",t);
		printPA(poly->rings[t]);
	}
	lwnotice("}");
}

int
lwpoly_compute_box2d_p(LWPOLY *poly, BOX2DFLOAT4 *box)
{
	BOX2DFLOAT4 boxbuf;
	uint32 i;

	if ( ! poly->nrings ) return 0;
	if ( ! ptarray_compute_box2d_p(poly->rings[0], box) ) return 0;
	for (i=1; i<poly->nrings; i++)
	{
		if ( ! ptarray_compute_box2d_p(poly->rings[0], &boxbuf) )
			return 0;
		if ( ! box2d_union_p(box, &boxbuf, box) )
			return 0;
	}
	return 1;
}

/* Clone LWLINE object. POINTARRAY are not copied, it's ring array is. */
LWPOLY *
lwpoly_clone(const LWPOLY *g)
{
	LWPOLY *ret = lwalloc(sizeof(LWPOLY));
	memcpy(ret, g, sizeof(LWPOLY));
	ret->rings = lwalloc(sizeof(POINTARRAY *)*g->nrings);
	memcpy(ret->rings, g->rings, sizeof(POINTARRAY *)*g->nrings);
	if ( g->bbox ) ret->bbox = box2d_clone(g->bbox);
	return ret;
}

/*
 * Add 'what' to this poly at position 'where'.
 * where=0 == prepend
 * where=-1 == append
 * Returns a MULTIPOLYGON or a GEOMETRYCOLLECTION
 */
LWGEOM *
lwpoly_add(const LWPOLY *to, uint32 where, const LWGEOM *what)
{
	LWCOLLECTION *col;
	LWGEOM **geoms;
	int newtype;

	if ( where != -1 && where != 0 )
	{
		lwerror("lwpoly_add only supports 0 or -1 as second argument, got %d", where);
		return NULL;
	}

	/* dimensions compatibility are checked by caller */

	/* Construct geoms array */
	geoms = lwalloc(sizeof(LWGEOM *)*2);
	if ( where == -1 ) /* append */
	{
		geoms[0] = lwgeom_clone((LWGEOM *)to);
		geoms[1] = lwgeom_clone(what);
	}
	else /* prepend */
	{
		geoms[0] = lwgeom_clone(what);
		geoms[1] = lwgeom_clone((LWGEOM *)to);
	}

	/* reset SRID and wantbbox flag from component types */
	geoms[0]->SRID = geoms[1]->SRID = -1;
	TYPE_SETHASSRID(geoms[0]->type, 0);
	TYPE_SETHASSRID(geoms[1]->type, 0);
	TYPE_SETHASBBOX(geoms[0]->type, 0);
	TYPE_SETHASBBOX(geoms[1]->type, 0);

	/* Find appropriate geom type */
	if ( TYPE_GETTYPE(what->type) == POLYGONTYPE ) newtype = MULTIPOLYGONTYPE;
	else newtype = COLLECTIONTYPE;

	col = lwcollection_construct(newtype,
		to->SRID, NULL,
		2, geoms);
	
	return (LWGEOM *)col;
}

void
lwpoly_forceRHR(LWPOLY *poly)
{
	int i;

	if ( ptarray_isccw(poly->rings[0]) )
	{
		ptarray_reverse(poly->rings[0]);
	}

	for (i=1; i<poly->nrings; i++)
	{
		if ( ! ptarray_isccw(poly->rings[i]) )
		{
			ptarray_reverse(poly->rings[i]);
		}
	}
}

void
lwpoly_release(LWPOLY *lwpoly)
{
  lwgeom_release(lwpoly_as_lwgeom(lwpoly));
}

void
lwpoly_reverse(LWPOLY *poly)
{
	int i;

	for (i=0; i<poly->nrings; i++)
		ptarray_reverse(poly->rings[i]);
}

LWPOLY *
lwpoly_segmentize2d(LWPOLY *poly, double dist)
{
	POINTARRAY **newrings;
	unsigned int i;
	
	newrings = lwalloc(sizeof(POINTARRAY *)*poly->nrings);
	for (i=0; i<poly->nrings; i++)
	{
		newrings[i] = ptarray_segmentize2d(poly->rings[i], dist);
	}
	return lwpoly_construct(poly->SRID, NULL,
		poly->nrings, newrings);
}

/*
 * check coordinate equality 
 * ring and coordinate order is considered
 */
char
lwpoly_same(const LWPOLY *p1, const LWPOLY *p2)
{
	unsigned int i;

	if ( p1->nrings != p2->nrings ) return 0;
	for (i=0; i<p1->nrings; i++)
	{
		if ( ! ptarray_same(p1->rings[i], p2->rings[i]) )
			return 0;
	}
	return 1;
}

/*
 * Construct a polygon from a LWLINE being
 * the shell and an array of LWLINE (possibly NULL) being holes.
 * Pointarrays from intput geoms are cloned.
 * SRID must be the same for each input line.
 * Input lines must have at least 4 points, and be closed.
 */
LWPOLY *
lwpoly_from_lwlines(const LWLINE *shell,
	unsigned int nholes, const LWLINE **holes)
{
	unsigned int nrings;
	POINTARRAY **rings = lwalloc((nholes+1)*sizeof(POINTARRAY *));
	int SRID = shell->SRID;
	LWPOLY *ret;

	if ( shell->points->npoints < 4 )
		lwerror("lwpoly_from_lwlines: shell must have at least 4 points");
	if ( ! ptarray_isclosed2d(shell->points) )
		lwerror("lwpoly_from_lwlines: shell must be closed");
	rings[0] = ptarray_clone(shell->points);

	for (nrings=1; nrings<=nholes; nrings++)
	{
		const LWLINE *hole = holes[nrings-1];

		if ( hole->SRID != SRID )
			lwerror("lwpoly_from_lwlines: mixed SRIDs in input lines");

		if ( hole->points->npoints < 4 )
			lwerror("lwpoly_from_lwlines: holes must have at least 4 points");
		if ( ! ptarray_isclosed2d(hole->points) )
			lwerror("lwpoly_from_lwlines: holes must be closed");

		rings[nrings] = ptarray_clone(hole->points);
	}

	ret = lwpoly_construct(SRID, NULL, nrings, rings);
	return ret;
}
