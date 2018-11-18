//
//  CRF++ -- Yet Another CRF toolkit
//
//  $Id: crf_test.cpp 1587 2007-02-12 09:00:36Z taku $;
//
//  Copyright(C) 2005-2007 Taku Kudo <taku@chasen.org>
//
#include "crfpp.h"
#include "winmain.h"
#include <iostream>
#include "crfpp.h"

int main(int argc, char **argv) {
	int code = crfpp_test(argc, argv);
<<<<<<< .mine
	if (code != 0) {
		std:cerr << "Last Error : " << CRFPP::getLastError()
	}
||||||| .r552
=======
	if (code != 0)
		std::cerr << "global error : " << CRFPP::getLastError() << " code = " << code << std::endl;
>>>>>>> .r584
	return code;
}
