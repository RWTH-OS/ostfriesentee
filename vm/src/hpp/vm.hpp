#ifndef VM_HPP
#define VM_HPP

#include "infusion.hpp"

namespace ostfriesentee {

class Vm {
	dj_vm* vm;

public:
	Vm() {
		this->vm = dj_vm_create();
	}

	~Vm() {
		dj_vm_destroy(this->vm);
	}

	void makeActiveVm() {
		dj_exec_setVM(this->vm);
	}


	void loadInfusionArchive(dj_archive& archive,
			dj_named_native_handler* handlers, size_t numberOfHandlers) {
		dj_vm_loadInfusionArchive(this->vm, &archive, handlers, numberOfHandlers);
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
