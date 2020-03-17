#ifndef DLLEXPORT_H
#define DLLEXPORT_H

#ifdef _WIN32 || _WIN64
    #define Q_DECL_EXPORT __declspec(dllexport)
    #define Q_DECL_IMPORT __declspec(dllimport)
#else
    #define Q_DECL_EXPORT
    #define Q_DECL_IMPORT
#endif

#if defined(ARRAYPART_LIBRARY)
#  define ARRAYPART_EXPORT Q_DECL_EXPORT
#else
#  define ARRAYPART_EXPORT Q_DECL_IMPORT
#endif

#endif // DLLEXPORT_H
