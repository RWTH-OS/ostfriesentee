#ifndef OBJECT_HPP
#define OBJECT_HPP

#include <hpp/vm.hpp>

namespace ostfriesentee {

class Object {
protected:
	dj_infusion* infusion;
	dj_object* obj;

public:
	ref_t getRef() {
		return VOIDP_TO_REF((void*)this->obj);
	}

protected:
	Object(Infusion& infusion) {
		this->infusion = infusion.getUnderlying();
		dj_mem_addSafePointer((void**)&this->infusion);
	}

	/// returns the implementation id of the first method that fits the
	/// definition id
	inline uint8_t findMethod(Infusion& baseInfusion, Infusion& derrivedInfusion,
			uint8_t classId, dj_local_id baseLocalDefinitionId) {
		// to quote the Darjeeling creators: "holy zombiejesus this is ugly"
		// map base local id to global id
		dj_global_id globalDefinitionId =
			dj_global_id_resolve(baseInfusion.getUnderlying(), baseLocalDefinitionId);
		// map global id to derrived local id
		dj_local_id definitionId =
			dj_global_id_mapToInfusion(globalDefinitionId, derrivedInfusion.getUnderlying());

		// iterate over methods
		dj_di_pointer classDef =
			dj_infusion_getClassDefinition(derrivedInfusion.getUnderlying(), classId);
		dj_di_pointer methodTable = dj_di_classDefinition_getMethodTable(classDef);

		for(uint8_t ii=0; ii<dj_di_methodTable_getSize(methodTable); ii++) {
			dj_di_pointer methodTableEntry = dj_di_methodTable_getEntry(methodTable, ii);

			// check if the definition matches the one of the base class
			if((dj_di_methodTableEntry_getDefinitionEntity(methodTableEntry) == definitionId.entity_id) &&
				(dj_di_methodTableEntry_getDefinitionInfusion(methodTableEntry)==definitionId.infusion_id) )
			{
				// return local (in the derrived infusion) implementation id
				const uint8_t implId =
					dj_di_methodTableEntry_getImplementationEntity(methodTableEntry);
				return implId;
			}
		}
		return 0;	// ERROR: not found
	}

	inline dj_global_id resolveVirtual(dj_local_id methodDefinitionLocalId) {
		dj_global_id methodDefGolbalId = dj_global_id_resolve(this->infusion, methodDefinitionLocalId);
		return dj_global_id_lookupVirtualMethod(methodDefGolbalId, this->obj);
	}

	template<size_t N0, size_t N1>
	inline void runVirtualMethod(dj_local_id methodDefinitionLocalId, ref_t (&refParams)[N0], int16_t (&intParams)[N1]) {
		dj_global_id method = this->resolveVirtual(methodDefinitionLocalId);
		dj_exec_callMethodFromNative(method, getThread(), &refParams[N0-1], intParams);
		// TODO: run untill method finished
		dj_exec_run(100000);
	}

	template<size_t N0>
	inline void runVirtualMethod(dj_local_id methodDefinitionLocalId, ref_t (&refParams)[N0]) {
		dj_global_id method = this->resolveVirtual(methodDefinitionLocalId);
		dj_exec_callMethodFromNative(method, getThread(), &refParams[N0-1], nullptr);
		// TODO: run untill method finished
		dj_exec_run(100000);
	}

	template<size_t N0, size_t N1>
	inline void runMethod(uint8_t methodId, ref_t (&refParams)[N0], int16_t (&intParams)[N1]) {
		dj_global_id method{this->infusion, methodId};
		dj_exec_callMethodFromNative(method, getThread(), &refParams[N0-1], intParams);
		// TODO: run untill method finished
		dj_exec_run(100000);
	}

	template<size_t N0>
	inline void runMethod(uint8_t methodId, ref_t (&refParams)[N0]) {
		dj_global_id method{this->infusion, methodId};
		dj_exec_callMethodFromNative(method, getThread(), &refParams[N0-1], nullptr);
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

public:
	template<size_t N0, size_t N1>
	static inline void runMethod(Infusion& inf, uint8_t methodId, ref_t (&refParams)[N0], int16_t (&intParams)[N1]) {
		dj_global_id method{inf.getUnderlying(), methodId};
		dj_exec_callMethodFromNative(method, getThread(), &refParams[N0-1], intParams);
		// TODO: run untill method finished
		dj_exec_run(100000);
	}

	template<size_t N0>
	static inline void runMethod(Infusion& inf, uint8_t methodId, ref_t (&refParams)[N0]) {
		dj_global_id method{inf.getUnderlying(), methodId};
		dj_exec_callMethodFromNative(method, getThread(), &refParams[N0-1], nullptr);
		// TODO: run untill method finished
		dj_exec_run(100000);
	}

	template<size_t N>
	static inline void setParam(ref_t (&refParams)[N], size_t index, ref_t value) {
		// ref stack is bottom to top
		refParams[(N-1) - index] = value;
	}

	template<size_t N>
	static inline void setParam(ref_t (&refParams)[N], size_t index, void* value) {
		// ref stack is bottom to top
		refParams[(N-1) - index] = VOIDP_TO_REF(value);
	}

	template<size_t N>
	static inline void setParam(ref_t (&refParams)[N], size_t index, Object& value) {
		// ref stack is bottom to top
		refParams[(N-1) - index] = value.getRef();
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
