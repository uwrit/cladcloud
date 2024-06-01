/*
 * Written by Ralph Mason ralph.mason<at>telogis.com
 *
 * Copyright Telogis 2004
 * www.telogis.com
 *
 */

#ifndef _WKTPARSE_H
#define _WKTPARSE_H

#include <stdlib.h>


#ifndef _LIBLWGEOM_H
typedef unsigned char uchar;

typedef struct serialized_lwgeom {
    uchar *lwgeom;
    int size;
} SERIALIZED_LWGEOM;

typedef struct struct_lwgeom_parser_result
{
	const char *wkinput;
        SERIALIZED_LWGEOM *serialized_lwgeom;
        int size;
        const char *message;
        int errlocation;
} LWGEOM_PARSER_RESULT;

typedef struct struct_lwgeom_unparser_result
{
	uchar *serialized_lwgeom;
        char *wkoutput;
        int size;
	const char *message;
        int errlocation;
} LWGEOM_UNPARSER_RESULT;
#endif
typedef void* (*allocator)(size_t size);
typedef void  (*freeor)(void* mem);
typedef void  (*report_error)(const char* string, ...);

/*typedef unsigned long int4;*/

/* How much memory is allocated at a time(bytes) for tuples */
#define ALLOC_CHUNKS 8192

/* to shrink ints less than 0x7f to 1 byte */
/* #define SHRINK_INTS */

#define	POINTTYPE	1
#define	LINETYPE	2
#define	POLYGONTYPE	3
#define	MULTIPOINTTYPE	4
#define	MULTILINETYPE	5
#define	MULTIPOLYGONTYPE	6
#define	COLLECTIONTYPE	7

/* Extended lwgeom integer types */
#define POINTTYPEI    10
#define LINETYPEI     11
#define POLYGONTYPEI  12

#define CIRCSTRINGTYPE       8
#define COMPOUNDTYPE    9
#define CURVEPOLYTYPE   13
#define MULTICURVETYPE          14
#define MULTISURFACETYPE        15

extern int srid;

/*

   These functions are used by  the
   generated parser and are not meant
   for public use

*/

void set_srid(double srid);
void alloc_lwgeom(int srid);

void alloc_point_2d(double x,double y);
void alloc_point_3d(double x,double y,double z);
void alloc_point_4d(double x,double y,double z,double m);

void alloc_point(void);
void alloc_linestring(void);
void alloc_linestring_closed(void);
void alloc_circularstring(void);
void alloc_circularstring_closed(void);
void alloc_polygon(void);
void alloc_compoundcurve(void);
void alloc_curvepolygon(void);
void alloc_multipoint(void);
void alloc_multilinestring(void);
void alloc_multicurve(void);
void alloc_multipolygon(void);
void alloc_multisurface(void);
void alloc_geomertycollection(void);
void alloc_empty();
void alloc_counter(void);


void pop(void);
void popc(void);

void alloc_wkb(const char* parser);

/*
	Use these functions to parse and unparse lwgeoms
	You are responsible for freeing the returned memory.
*/

int parse_lwg(LWGEOM_PARSER_RESULT *lwg_parser_result, const char* wkt, int flags, allocator allocfunc,report_error errfunc);
int parse_lwgi(LWGEOM_PARSER_RESULT *lwg_parser_result, const char* wkt, int flags, allocator allocfunc,report_error errfunc);
int unparse_WKT(LWGEOM_UNPARSER_RESULT *lwg_unparser_result, uchar* serialized, allocator alloc, freeor free, int flags);
int unparse_WKB(LWGEOM_UNPARSER_RESULT *lwg_unparser_result, uchar* serialized, allocator alloc, freeor free, int flags, char endian, uchar hexform);
int lwg_parse_yyparse(void);
int lwg_parse_yyerror(char* s);
void lwg_parse_yynotice(char* s);


#endif /* _WKTPARSE_H */
