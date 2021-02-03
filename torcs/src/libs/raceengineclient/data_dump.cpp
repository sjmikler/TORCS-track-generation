#include "data_dump.h"
#include <ctime>

FILE *dataFile = NULL;
const int MAX_PLAYERS = 64;
float lastDump[MAX_PLAYERS];

const float dumpDelta = 0.049f;
const char CSV_HEADER[] = "time,driver_id,driver_name,position,lap,vx,vy,vz";

void dataDump(tRmInfo *ReInfo, tCarElt *car)
{
	if (dataFile == NULL) {
		return;
	}
	double currentTime = ReInfo->s->currentTime;
	if (currentTime < lastDump[car->index] + dumpDelta) {
		return;
	}
	lastDump[car->index] = currentTime;

	fprintf(dataFile, "%.4lf,%d,\"%s\",%d,%d,%f,%f,%f,\n",
		currentTime,
		car->index,
		car->_name,
		car->_pos,
		car->_laps,
		car->_speed_x,
		car->_speed_y,
		car->_speed_z
		);
}

void dataDumpInit(tRmInfo *ReInfo)
{
	time_t t = time(NULL);
	tm *stm = localtime(&t);
	const int DATA_PATH_SIZE = 1024;
	char dataPath[DATA_PATH_SIZE];
	snprintf(dataPath, DATA_PATH_SIZE, "%sresults/%s/data-%4d-%02d-%02d-%02d-%02d-%02d.csv",
		GetLocalDir(),
		ReInfo->_reFilename,
		stm->tm_year+1900,
		stm->tm_mon+1,
		stm->tm_mday,
		stm->tm_hour,
		stm->tm_min,
		stm->tm_sec
	);
	GfCreateDirForFile(dataPath);
	dataFile = fopen(dataPath, "w");
	fprintf(dataFile, "%s\n", CSV_HEADER);

    for (int i = 0; i < MAX_PLAYERS; i++) {
        lastDump[i] = -99999.0f;
    }
}

void dataDumpCleanup()
{
	if (dataFile != NULL) {
		fclose(dataFile);
		dataFile = NULL;
	}
}
