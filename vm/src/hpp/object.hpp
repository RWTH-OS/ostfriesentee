#ifndef OBJECT_HPP
#define OBJECT_HPP

#include <hpp/vm.hpp>

namespace ostfriesentee {

class Object {
protected:
	dj_infusion* infusion;

	Object(Infusion& infusion) {
		this->infusion = infusion.getUnderlying();
	}

	template<size_t N0, size_t N1>
	inline void runMethod(uint8_t methodId, ref_t (&refParams)[N0], int16_t (&intParams)[N1]) {
		dj_global_id method{this->infusion, methodId};
		dj_exec_callMethodFromNative(method, getThread(), refParams, intParams);
		// TODO: run untill method finished
		dj_exec_run(100000);
	}

	/// creates a dj_object instance
	static inline dj_object* create(dj_infusion* infusion, uint8_t classId) {
		dj_global_id id {infusion, classId};
		uint8_t runtime_id = dj_global_id_getRuntimeClassId(id);
		dj_di_pointer classDef =
			dj_vm_getRuntimeClassDefinition(dj_exec_getVM(), runtime_id);
		dj_object* obj = dj_object_create(runtime_id,
				dj_di_classDefinition_getNrRefs(classDef),
				dj_di_classDefinition_getOffsetOfFirstReference(classDef)
				);
		return obj;
	}

	static inline dj_thread* getThread() {
		dj_vm* vm = dj_exec_getVM();
		if(vm->threads == nullptr) {
			vm->threads = dj_thread_create();
		}
		return vm->threads;
	}

	template<size_t N>
	static inline void setParam(ref_t (&refParams)[N], size_t index, ref_t value) {
		refParams[index] = value;
	}

	template<size_t N>
	static inline void setParam(ref_t (&refParams)[N], size_t index, void* value) {
		refParams[index] = VOIDP_TO_REF(value);
	}

	template<size_t N>
	static inline void setParam(int16_t (&intParams)[N], size_t index, bool value) {
		intParams[index] = static_cast<int16_t>(value);
	}

	template<size_t N>
	static inline void setParam(int16_t (&intParams)[N], size_t index, int8_t value) {
		intParams[index] = static_cast<int16_t>(value);
	}

	template<size_t N>
	static inline void setParam(int16_t (&intParams)[N], size_t index, int16_t value) {
		intParams[index] = value;
	}

	template<size_t N>
	static inline void setParam(int16_t (&intParams)[N], size_t index, int32_t value) {
		intParams[index+0] = (value >>  0) & 0xffff;
		intParams[index+1] = (value >> 16) & 0xffff;
	}

	template<size_t N>
	static inline void setParam(int16_t (&intParams)[N], size_t index, int64_t value) {
		intParams[index+0] = (value >>  0) & 0xffff;
		intParams[index+1] = (value >> 16) & 0xffff;
		intParams[index+2] = (value >> 32) & 0xffff;
		intParams[index+3] = (value >> 48) & 0xffff;
	}
};


} // namespace ostfriesentee


#endif // OBJECT_HPP
