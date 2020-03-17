#TEMPLATE = app
TEMPLATE = lib

TARGET = array_part
#CONFIG += console

DEPENDPATH += .
INCLUDEPATH += .

DESTDIR = ../array_part

DEFINES += ARRAYPART_LIBRARY

CONFIG -= qt
CONFIG += dll

QT -= core gui

HEADERS += \
    array_part.h \
    dllexport.h

SOURCES += \
    array_part.cpp \
    main.cpp
