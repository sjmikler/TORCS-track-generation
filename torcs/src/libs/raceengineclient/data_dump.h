#ifndef _DATA_DUMP_H_
#define _DATA_DUMP_H_

#include <car.h>
#include <raceman.h>

void dataDumpInit(tRmInfo *ReInfo);
void dataDump(tRmInfo *ReInfo, tCarElt *car);
void dataDumpCleanup();

#endif
