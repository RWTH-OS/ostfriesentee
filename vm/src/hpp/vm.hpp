#ifndef VM_HPP
#define VM_HPP

#include "infusion.hpp"

namespace ostfriesentee {

class Vm {
	dj_vm* vm;

public:
	Vm() : vm(nullptr) {}

	~Vm() {
		if(this->vm != nullptr) {
			dj_vm_destroy(this->vm);
		}
	}

	template<size_t N>
	void initialize(uint8_t (&mem)[N]) {
		dj_mem_init(mem, N);
		ref_t_base_address = (char*)mem - 42;
		this->vm = dj_vm_create();
	}

	// the first thread is used for calling Java methods from native
	dj_thread* getFirstThread() {
		if(this->vm->threads == nullptr) {
			this->vm->threads = dj_thread_create();
		}
		return this->vm->threads;
	}

	void makeActiveVm() {
		dj_exec_setVM(this->vm);
	}

	void loadInfusionArchive(dj_archive& archive,
			dj_named_native_handler* handlers, size_t numberOfHandlers) {
		dj_vm_loadInfusionArchive(this->vm, &archive, handlers, numberOfHandlers);
	}

	Infusion loadInfusion(const uint8_t* di) {
		auto inf = dj_vm_loadInfusion(this->vm, reinterpret_cast<dj_di_pointer>(di));
		Infusion infusion(inf);
		return infusion;
	}

	int countLiveThreads() {
		return dj_vm_countLiveThreads(this->vm);
	}

	void schedule() {
		dj_vm_schedule(vm);
	}

	dj_object * createSysLibObject(uint8_t entity_id) {
		return dj_vm_createSysLibObject(this->vm, entity_id);
	}

	dj_di_pointer getRuntimeClassDefinition(const uint8_t runtimeId) {
		return dj_vm_getRuntimeClassDefinition(this->vm, runtimeId);
	}

	void addThread(dj_thread* thread) const {
		dj_vm_addThread(this->vm, thread);
	}

	void activateThread(dj_thread* thread) const {
		dj_vm_activateThread(this->vm, thread);
	}

	/// executes blocking until all threads are dead
	void run() {
		while (this->countLiveThreads()>0)
		{
			this->schedule();
			if (this->vm->currentThread!=NULL)
				if (this->vm->currentThread->status==THREADSTATUS_RUNNING)
					dj_exec_run(RUNSIZE);
		}
	}

	Infusion firstInfusion() {
		Infusion inf(this->vm->infusions);
		return inf;
	}
};

} // namespace ostfriesentee
#endif // VM_HPP
