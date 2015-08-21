/*
 * vmthread.c
 * 
 * Copyright (c) 2008-2010 CSIRO, Delft University of Technology.
 * 
 * This file is part of Darjeeling.
 * 
 * Darjeeling is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Darjeeling is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with Darjeeling.  If not, see <http://www.gnu.org/licenses/>.
 */
 
#include <string.h>

#include "types.h"
#include "vmthread.h"
#include "heap.h"
#include "vm.h"
#include "execution.h"
#include "djtimer.h"
#include "debug.h"
#include "global_id.h"

//platform-specific
#include "config.h"

// generated by the infuser
#include "jlib_base.h"

/**
 * Creates a new dj_thread object, and constructs a new frame for the given infusion and
 * methodImplementation, which is pushed onto the thread's frame stack. Basically this method gives
 * the caller a ready-to-run thread.
 * @param infusion the infusion context for the top frame in the newly created thread
 * @param methodImplementation the method to run in the newly created thread
 * @return a newly created dj_thread object, or null in case of fail (out of memory)
 */
dj_thread *dj_thread_create_and_run(dj_global_id methodImplId)
{
	// create the top frame for the given method
	dj_frame *frame = dj_frame_create(methodImplId);

	// if we're out of memory, let the caller deal with it
    if (frame==NULL)
    {
        DEBUG_LOG("dj_thread_create_and_run: could not create top frame. Returning null\n");
        return NULL;
    }

    dj_mem_addSafePointer((void**)&frame);

	// create a thread to execute the method in
	dj_thread *ret = dj_thread_create();

	// if we're out of memory, let the caller deal with it
    if (ret==NULL)
    {
        // free the frame object (if we get here, its allocation was successful)
        DEBUG_LOG("dj_thread_create_and_run: could create the top frame but not the Thread object. Aborting\n");
        dj_mem_free(frame);

    } else
    {
    	ret->frameStack = frame;
    	ret->status = THREADSTATUS_RUNNING;
    }

	dj_mem_removeSafePointer((void**)&frame);

	return ret;
}

/**
 * Creates a new dj_thread object.
 * @return a new dj_tread object, or null if fail (out of memory)
 */
dj_thread *dj_thread_create()
{
	dj_thread *ret = (dj_thread*)dj_mem_alloc(sizeof(dj_thread), CHUNKID_THREAD);

	// if we're out of memory, let the caller handle it
	if (ret==NULL)
    {
        DEBUG_LOG("dj_thread_create: could not create Thread object frame. Returning null\n");
        return NULL;
    }

	// init thread properties
	ret->frameStack = NULL;
	ret->status = THREADSTATUS_CREATED;
	ret->scheduleTime = 0;
	ret->id = 0;
	ret->next = NULL;
	ret->priority = 0;
	ret->runnable = NULL;
	ret->monitorObject = NULL;
	ret->referenceParameters = NULL;
	ret->integerParameters = NULL;

	return ret;
}

void dj_thread_destroy(dj_thread *thread)
{
	dj_mem_free(thread);
}

/**
 * Pushes a new stack frame onto the stack. Used by the execution engine to enter methods.
 * @param thread the thread to push the frame onto
 * @param frame the frame to push
 */
void dj_thread_pushFrame(dj_thread *thread, dj_frame *frame)
{
	frame->parent = thread->frameStack;
	thread->frameStack = frame;
}

/**
 * Pops a stack frame from the frame stack. Used by the execution engine to leave methods and throw
 * exceptions.
 * @param thread the thread to pop a stack frame from
 * @return the popped frame
 */
dj_frame *dj_thread_popFrame(dj_thread *thread)
{
	dj_frame *ret = thread->frameStack;
	thread->frameStack = thread->frameStack->parent;
	return ret;
}

void dj_frame_markRootSet(dj_frame *frame)
{
	int i;
	ref_t *stack, *locals;

	// Mark the frame object as BLACK (don't collect, don't inspect further)
	dj_mem_setChunkColor(frame, TCM_BLACK);

	// Mark every object on the reference stack
	stack = dj_frame_getReferenceStack(frame);
	for (i=0; i<frame->nr_ref_stack; i++)
		dj_mem_setRefGrayIfWhite(stack[i]);

	// Mark every object in the local variables
	locals = dj_frame_getLocalReferenceVariables(frame);
	for (i=0; i<dj_di_methodImplementation_getReferenceLocalVariableCount(dj_global_id_getMethodImplementation(frame->method)); i++)
		dj_mem_setRefGrayIfWhite(locals[i]);

}

void dj_frame_updatePointers(dj_frame * frame)
{
	int i;
	ref_t *stack, *locals;

	// Update references on the reference stack
	stack = dj_frame_getReferenceStack(frame);
	for (i=0; i<frame->nr_ref_stack; i++)
		stack[i] = dj_mem_getUpdatedReference(stack[i]);

	// Update the local variables
	locals = dj_frame_getLocalReferenceVariables(frame);
	for (i=0; i<dj_di_methodImplementation_getReferenceLocalVariableCount(dj_global_id_getMethodImplementation(frame->method)); i++)
		locals[i] = dj_mem_getUpdatedReference(locals[i]);

	// update pointers to the infusion and parent frame
	// NOTE these have to be updated AFTER the stack and local variable frame
	frame->method.infusion = dj_mem_getUpdatedPointer(frame->method.infusion);
	DEBUG_LOG("parent is changed from %p to %p\n", frame->parent, dj_mem_getUpdatedPointer(frame->parent));
	frame->parent = dj_mem_getUpdatedPointer(frame->parent);

}

void dj_thread_markRootSet(dj_thread *thread)
{
	dj_frame *frame;

	// mark the thread object as BLACK (don't collect, don't inspect further)
	// finished threads may be reclaimed by the GC
	if (thread->status!=THREADSTATUS_FINISHED)
		dj_mem_setChunkColor(thread, TCM_BLACK);

	// mark the thread's monitor object and name string as GRAY
	if (thread->monitorObject!=NULL) dj_mem_setRefGrayIfWhite(VOIDP_TO_REF(thread->monitorObject));
	if (thread->runnable!=NULL) dj_mem_setRefGrayIfWhite(VOIDP_TO_REF(thread->runnable));

	// mark each of the frames
	frame = thread->frameStack;
	while (frame!=NULL)
	{
		dj_frame_markRootSet(frame);
		frame = frame->parent;
	}
}

void dj_thread_updatePointers(dj_thread * thread)
{
	thread->frameStack = dj_mem_getUpdatedPointer(thread->frameStack);
	thread->monitorObject = dj_mem_getUpdatedPointer(thread->monitorObject);
	thread->next = dj_mem_getUpdatedPointer(thread->next);
	thread->runnable = dj_mem_getUpdatedPointer(thread->runnable);
}


/**
 * Puts a thread to sleep. Sets the state of the thread to THREADSTATUS_SLEEPING and sets its timer to
 * the given timeout.
 * @param thread the thread to sleep
 * @param time the number of milliseconds to sleep
 */
void dj_thread_sleep(dj_thread *thread, dj_time_t time)
{
	dj_time_t sleepTime = dj_timer_getTimeMillis() + time;
	thread->status = THREADSTATUS_SLEEPING;
	thread->scheduleTime = sleepTime;
}

void dj_thread_wait(dj_thread * thread, dj_object * object, dj_time_t time)
{
	thread->status = THREADSTATUS_WAITING_FOR_MONITOR;
	thread->scheduleTime = time==0?0:(dj_timer_getTimeMillis() + time);
	thread->monitorObject = object;
}


/**
 * Creates a new dj_frame object for a given method implementation.
 * @param methodImplId the method implementation this frame will be executing
 * @return a newly created dj_frame object, or null if fail (out of memory)
 */
dj_frame *dj_frame_create(dj_global_id methodImplId)
{
	dj_infusion * infusion = methodImplId.infusion;
	dj_mem_addSafePointer((void**)&infusion);

	dj_di_pointer methodImpl = dj_global_id_getMethodImplementation(methodImplId);

	// calculate the size of the frame to create
	int localVariablesSize =
		(dj_di_methodImplementation_getReferenceLocalVariableCount(methodImpl) * sizeof(ref_t)) +
		(dj_di_methodImplementation_getIntegerLocalVariableCount(methodImpl) * sizeof(int16_t));

	int size =
		sizeof(dj_frame) +
		(dj_di_methodImplementation_getMaxStack(methodImpl) * sizeof(int16_t)) +
		localVariablesSize
		;

	dj_frame *ret = (dj_frame*)dj_mem_alloc(size, CHUNKID_FRAME);

	// in case of null, return and let the caller deal with it
	if (ret==NULL)
    {
        DEBUG_LOG("dj_frame_create: could not create frame. Returning null\n");
    } else
    {
    	// restore a potentially invalid infusion pointer
    	methodImplId.infusion = infusion;

		// init the frame
		ret->method = methodImplId;
		ret->parent = NULL;
		ret->pc = 0;
		ret->nr_int_stack = 0;
		ret->nr_ref_stack = 0;

		// set local variables to 0/null
		memset(dj_frame_getLocalReferenceVariables(ret), 0, localVariablesSize);
    }

	dj_mem_removeSafePointer((void**)&infusion);

	return ret;
}

/**
 * Creates a new monitor block.
 * @return a newly created monitor block, or null if failed (out of memory)
 */
dj_monitor_block * dj_monitor_block_create()
{
	dj_monitor_block * ret = (dj_monitor_block *)dj_mem_alloc(sizeof(dj_monitor_block), CHUNKID_MONITOR_BLOCK);
	if (ret==NULL) return NULL;

    memset(ret, 0, sizeof(dj_monitor_block));

	return ret;
}

void dj_monitor_block_updatePointers(dj_monitor_block * monitor_block)
{
	int i;
	monitor_block->next = dj_mem_getUpdatedPointer(monitor_block->next);
	for (i=0; i<monitor_block->count; i++)
	{
		monitor_block->monitors[i].object = dj_mem_getUpdatedPointer(monitor_block->monitors[i].object);
		monitor_block->monitors[i].owner = dj_mem_getUpdatedPointer(monitor_block->monitors[i].owner);
	}
}

void dj_monitor_markRootSet(dj_monitor_block * monitor_block)
{
	int i;

	// Mark the monitor object as BLACK (don't collect, don't inspect further)
	dj_mem_setChunkColor(monitor_block, TCM_BLACK);

	for (i=0; i<monitor_block->count; i++)
		dj_mem_setRefGrayIfWhite(VOIDP_TO_REF(monitor_block->monitors[i].object));

}

