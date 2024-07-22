# Turning the R Degauss Geocoder implementation into an API for servicing a single address

Pulling from here:  https://github.com/degauss-org/geocoder/tree/master

Slapping a copy of the Flask API implementation on top of that based on UW Geocoder approach.

Here we are also adapting the Ubuntu impementation into an Alpine approach.


## Usage 

```
$ curl http://cladgeocoder.rit.uw.edu:50008/degausslatlong?q=1410+NE+Campus+Parkway%2c+Seattle%2c+WA+98195

[{"street":"NE Campus Pkwy","zip":"98195","city":"Seattle","state":"WA","lat":47.656234,"lon":-122.315577,"fips_county":"53033","score":0.806,"prenum":"","number":"1198","precision":"street"}]

```



## CVE Check 7-21-2024


```
jtl@rit-db-01 degauss-alpine % docker image ls
REPOSITORY                                      TAG        IMAGE ID       CREATED         SIZE
degauss-alpine-degaussalpine                    latest     698153d7566f   2 minutes ago   5.2GB
rhub/r-minimal                                  4.5.0      51e94ae92a91   19 hours ago    45MB
jtl@rit-db-01 degauss-alpine % trivy image 51e94ae92a91
2024-07-21T19:25:44-07:00	INFO	Need to update DB
2024-07-21T19:25:44-07:00	INFO	Downloading DB...	repository="ghcr.io/aquasecurity/trivy-db:2"
50.08 MiB / 50.08 MiB [--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------] 100.00% 3.63 MiB p/s 14s
2024-07-21T19:25:59-07:00	INFO	Vulnerability scanning is enabled
2024-07-21T19:25:59-07:00	INFO	Secret scanning is enabled
2024-07-21T19:25:59-07:00	INFO	If your scanning is slow, please try '--scanners vuln' to disable secret scanning
2024-07-21T19:25:59-07:00	INFO	Please see also https://aquasecurity.github.io/trivy/v0.53/docs/scanner/secret#recommendation for faster secret detection
2024-07-21T19:26:00-07:00	INFO	Detected OS	family="alpine" version="3.19.2"
2024-07-21T19:26:00-07:00	INFO	[alpine] Detecting vulnerabilities...	os_version="3.19" repository="3.19" pkg_num=36
2024-07-21T19:26:00-07:00	INFO	Number of language-specific files	num=0
2024-07-21T19:26:00-07:00	WARN	Using severities from other vendors for some vulnerabilities. Read https://aquasecurity.github.io/trivy/v0.53/docs/scanner/vulnerability#severity-selection for details.

51e94ae92a91 (alpine 3.19.2)

Total: 4 (UNKNOWN: 0, LOW: 0, MEDIUM: 4, HIGH: 0, CRITICAL: 0)

┌────────────┬───────────────┬──────────┬────────┬───────────────────┬───────────────┬────────────────────────────────────────────────┐
│  Library   │ Vulnerability │ Severity │ Status │ Installed Version │ Fixed Version │                     Title                      │
├────────────┼───────────────┼──────────┼────────┼───────────────────┼───────────────┼────────────────────────────────────────────────┤
│ libcrypto3 │ CVE-2024-4741 │ MEDIUM   │ fixed  │ 3.1.5-r0          │ 3.1.6-r0      │ openssl: Use After Free with SSL_free_buffers  │
│            │               │          │        │                   │               │ https://avd.aquasec.com/nvd/cve-2024-4741      │
│            ├───────────────┤          │        │                   │               ├────────────────────────────────────────────────┤
│            │ CVE-2024-5535 │          │        │                   │               │ openssl: SSL_select_next_proto buffer overread │
│            │               │          │        │                   │               │ https://avd.aquasec.com/nvd/cve-2024-5535      │
├────────────┼───────────────┤          │        │                   │               ├────────────────────────────────────────────────┤
│ libssl3    │ CVE-2024-4741 │          │        │                   │               │ openssl: Use After Free with SSL_free_buffers  │
│            │               │          │        │                   │               │ https://avd.aquasec.com/nvd/cve-2024-4741      │
│            ├───────────────┤          │        │                   │               ├────────────────────────────────────────────────┤
│            │ CVE-2024-5535 │          │        │                   │               │ openssl: SSL_select_next_proto buffer overread │
│            │               │          │        │                   │               │ https://avd.aquasec.com/nvd/cve-2024-5535      │
└────────────┴───────────────┴──────────┴────────┴───────────────────┴───────────────┴────────────────────────────────────────────────┘
jtl@rit-db-01 degauss-alpine % trivy image 698153d7566f
2024-07-21T19:26:27-07:00	INFO	Vulnerability scanning is enabled
2024-07-21T19:26:27-07:00	INFO	Secret scanning is enabled
2024-07-21T19:26:27-07:00	INFO	If your scanning is slow, please try '--scanners vuln' to disable secret scanning
2024-07-21T19:26:27-07:00	INFO	Please see also https://aquasecurity.github.io/trivy/v0.53/docs/scanner/secret#recommendation for faster secret detection
2024-07-21T19:29:48-07:00	INFO	Detected OS	family="alpine" version="3.19.2"
2024-07-21T19:29:48-07:00	INFO	[alpine] Detecting vulnerabilities...	os_version="3.19" repository="3.19" pkg_num=141
2024-07-21T19:29:48-07:00	INFO	Number of language-specific files	num=1
2024-07-21T19:29:48-07:00	INFO	[gemspec] Detecting vulnerabilities...
2024-07-21T19:29:48-07:00	WARN	Using severities from other vendors for some vulnerabilities. Read https://aquasecurity.github.io/trivy/v0.53/docs/scanner/vulnerability#severity-selection for details.

698153d7566f (alpine 3.19.2)

Total: 4 (UNKNOWN: 0, LOW: 0, MEDIUM: 4, HIGH: 0, CRITICAL: 0)

┌────────────┬───────────────┬──────────┬────────┬───────────────────┬───────────────┬────────────────────────────────────────────────┐
│  Library   │ Vulnerability │ Severity │ Status │ Installed Version │ Fixed Version │                     Title                      │
├────────────┼───────────────┼──────────┼────────┼───────────────────┼───────────────┼────────────────────────────────────────────────┤
│ libcrypto3 │ CVE-2024-4741 │ MEDIUM   │ fixed  │ 3.1.5-r0          │ 3.1.6-r0      │ openssl: Use After Free with SSL_free_buffers  │
│            │               │          │        │                   │               │ https://avd.aquasec.com/nvd/cve-2024-4741      │
│            ├───────────────┤          │        │                   │               ├────────────────────────────────────────────────┤
│            │ CVE-2024-5535 │          │        │                   │               │ openssl: SSL_select_next_proto buffer overread │
│            │               │          │        │                   │               │ https://avd.aquasec.com/nvd/cve-2024-5535      │
├────────────┼───────────────┤          │        │                   │               ├────────────────────────────────────────────────┤
│ libssl3    │ CVE-2024-4741 │          │        │                   │               │ openssl: Use After Free with SSL_free_buffers  │
│            │               │          │        │                   │               │ https://avd.aquasec.com/nvd/cve-2024-4741      │
│            ├───────────────┤          │        │                   │               ├────────────────────────────────────────────────┤
│            │ CVE-2024-5535 │          │        │                   │               │ openssl: SSL_select_next_proto buffer overread │
│            │               │          │        │                   │               │ https://avd.aquasec.com/nvd/cve-2024-5535      │
└────────────┴───────────────┴──────────┴────────┴───────────────────┴───────────────┴────────────────────────────────────────────────┘
jtl@rit-db-01 degauss-alpine %

```


