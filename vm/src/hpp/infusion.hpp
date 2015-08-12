#ifndef INFUSION_HPP
#define INFUSION_HPP

namespace ostfriesentee {

class Infusion {
	dj_infusion* inf;

public:
	Infusion(dj_infusion* infusion) {
		this->inf = infusion;
	}

	Infusion next() {
		Infusion next(this->inf->next);
		return next;
	}

	bool isValid() {
		return (this->inf != nullptr);
	}

	//------------------------------------------------------------------------
	// header operations

	uint8_t getMajorVersion() {
		return dj_di_header_getMajorVersion(this->inf->header);
	}

	uint8_t getMinorVersion() {
		return dj_di_header_getMinorVersion(this->inf->header);
	}

	uint8_t getEntryPoint() {
		return dj_di_header_getEntryPoint(this->inf->header);
	}

	char* getName() {
		return reinterpret_cast<char*>(dj_di_header_getInfusionName(this->inf->header));
	}

};

} // namespace ostfriesentee

#endif // INFUSION_HPP
