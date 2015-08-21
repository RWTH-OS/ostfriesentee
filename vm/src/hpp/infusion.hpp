#ifndef INFUSION_HPP
#define INFUSION_HPP

namespace ostfriesentee {

/// ostfriesentee strings are not null terminated, but
/// carry a size
struct String {
	char* data;
	uint16_t length;

	String(char* data, uint16_t length) : data(data), length(length) {}
	String(const dj_di_pointer data, uint16_t length) : 
		data(reinterpret_cast<char* >(data)), length(length) {}
};

class List {
	dj_di_pointer list;

	/// returns a ref_t that contains the offset of the element
	/// refered to by the index
	ref_t getOffset(const uint8_t index) const {
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
	dj_di_pointer getElement(const uint8_t index) const {
		return (this->list + this->getOffset(index));
	}

};

class ClassDefinition {
	dj_di_pointer classDef;

public:
	ClassDefinition(const dj_di_pointer classDef) {
		this->classDef = classDef;
	}

	uint8_t getNumberOfReferences() const {
		return dj_di_classDefinition_getNrRefs(this->classDef);
	}

	// TODO: resolve id
	dj_local_id getSuperClass() const {
		return dj_di_classDefinition_getSuperClass(this->classDef);
	}

	uint8_t getConstantInitMethodId() const {
		return dj_di_classDefinition_getCLInit(this->classDef);
	}

	dj_local_id getNameId() const {
		return dj_di_classDefinition_getClassName(this->classDef);
	}

	uint8_t getNumberOfInterfaces() const {
		return dj_di_classDefinition_getNrInterfaces(this->classDef);
	}

	// TODO: resolve id
	// index must be smaller than value returned by getNumberOfInterfaces()
	dj_local_id getInterface(uint8_t index) const {
		return dj_di_classDefinition_getInterface(this->classDef, index);
	}
};

class ClassList : public List {
public:
	ClassList(const dj_di_pointer list) : List(list) {}

	// index must be smaller than value returned by getSize()
	const ClassDefinition getElement(const uint8_t index) const {
		dj_di_pointer element = List::getElement(index);
		ClassDefinition def(element);
		return def;
	}
};

class StringTable {
	dj_di_pointer table;

public:
	StringTable(dj_di_pointer table) {
		this->table = table;
	}

	uint16_t getSize() {
		return dj_di_stringtable_getNrElements(this->table);
	}

	// index must be smaller than value returned by getSize()
	const String getString(const uint16_t index) {
		uint16_t length = dj_di_stringtable_getElementLength(this->table, index);
		const dj_di_pointer data = dj_di_stringtable_getElementBytes(this->table, index);
		const String str(data, length);
		return str;
	}
};


class Infusion {
	dj_infusion* inf;

public:
	Infusion(dj_infusion* infusion) {
		this->inf = infusion;
	}

	dj_infusion* getUnderlying() {
		return this->inf;
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
	const ClassList getClassList() {
		ClassList classList(this->inf->classList);
		return classList;
	}

	const List getMethodImplementationList() {
		List methodImplementationList(this->inf->methodImplementationList);
		return methodImplementationList;
	}

	const StringTable getStringTable() {
		StringTable strings(this->inf->stringTable);
		return strings;
	}
};

} // namespace ostfriesentee

#endif // INFUSION_HPP
