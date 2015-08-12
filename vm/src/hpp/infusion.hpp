#ifndef INFUSION_HPP
#define INFUSION_HPP

namespace ostfriesentee {


class List {
	dj_di_pointer list;

	/// returns a ref_t that contains the offset of the element
	/// refered to by the index
	const ref_t getOffset(const uint8_t index) const {
		// see dj_di_parentElement_getChild for why the `+1` is needed
		return dj_di_getListPointer(this->list + 1, index);
	}

public:
	List(const dj_di_pointer list) {
		this->list = list;
	}

	uint8_t getSize() const {
		return dj_di_parentElement_getListSize(this->list);
	}

	// index must be smaller than value returned by getSize()
	const dj_di_pointer getElement(const uint8_t index) const {
		return (this->list + this->getOffset(index));
	}

};

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

	//------------------------------------------------------------------------

	const List getClassList() {
		List classList(this->inf->classList);
		return classList;
	}

	const List getMethodImplementationList() {
		List methodImplementationList(this->inf->methodImplementationList);
		return methodImplementationList;
	}
};

} // namespace ostfriesentee

#endif // INFUSION_HPP
