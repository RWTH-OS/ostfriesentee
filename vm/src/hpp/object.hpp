#ifndef OBJECT_HPP
#define OBJECT_HPP

#include <hpp/vm.hpp>

namespace ostfriesentee {

class Object {
protected:
	/// creates a dj_object instance
	static inline dj_object* create(Vm& vm, dj_infusion* infusion, uint8_t classId) {
		dj_global_id id {infusion, classId};
		uint8_t runtime_id = dj_global_id_getRuntimeClassId(id);
		dj_di_pointer classDef = vm.getRuntimeClassDefinition(runtime_id);
		dj_object* obj = dj_object_create(runtime_id,
				dj_di_classDefinition_getNrRefs(classDef),
				dj_di_classDefinition_getOffsetOfFirstReference(classDef)
				);
		return obj;
	}
};


} // namespace ostfriesentee


#endif // OBJECT_HPP
