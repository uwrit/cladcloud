# Nominatim Docker (Nominatim version 4.4)

## Customized for Ubuntu 'Noble'

Upgrading to PHP 8.3 as 8.1 on default 'Jammy' has a number of high and critical CVE's and doesn't have default compatibility with 8.3.

'Noble' also only supports postgres 16 so Dockerfile and scripting updates were made to reflect that version change.