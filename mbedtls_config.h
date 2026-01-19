#ifndef MBEDTLS_CONFIG_H
#define MBEDTLS_CONFIG_H

// 1. System Support
// Tell mbedtls we are on a custom system (bare metal)
#define MBEDTLS_NO_PLATFORM_ENTROPY

// 2. Enable Algorithms
// We only need SHA-512 (which also enables SHA-384)
#define MBEDTLS_SHA512_C

#endif // MBEDTLS_CONFIG_H