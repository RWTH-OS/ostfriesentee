/*
 * debug.c
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
 
#include "types.h"
#include "array.h"
#include "panic.h"
#include "debug.h"
#include "vmthread.h"

#include "config.h"

/* Everything  interesting is  in debug.h,  but  we need  a couple  of
 * global variables.*/


static inline void print_size(const char* type_name, size_t size)
{
	size_t alignment =
		(size % 4 == 0)? 4 :
		(size % 2 == 0)? 2 : 1;
	DARJEELING_PRINTF("[%u-byte aligned] sizeof(%s)=%u bytes\n", alignment, type_name, size);
}

void dj_print_type_sizes()
{
	print_size("dj_local_id",  sizeof(dj_local_id));
	print_size("dj_global_id", sizeof(dj_global_id));
	print_size("dj_object",    sizeof(dj_object));
	print_size("dj_thread",    sizeof(dj_thread));
	print_size("dj_frame",     sizeof(dj_frame));
	print_size("dj_monitor",   sizeof(dj_monitor));
	print_size("dj_monitor_block", sizeof(dj_monitor_block));
	print_size("dj_infusion",  sizeof(dj_infusion));
	print_size("dj_vm",        sizeof(dj_vm));
	print_size("dj_named_native_handler", sizeof(dj_named_native_handler));
}


// though, we only need them when actually doing some debugging
#if defined(DARJEELING_DEBUG) || defined(DARJEELING_DEBUG_PERFILE)

int  darjeeling_debug_nesting_level=0;
int  darjeeling_debug_indent_index=0;
char darjeeling_debug_char_buffer[256];


// dumps the  stack frame, and  calls itself recursively to  print the
// whole execution stack

//TODO also dump the operand stack and the local variables (see
//execution.c for an example of that)
void dj_dump_stack(dj_frame *frame)
{
	// NB: commented this out because of the stack rearrangement stuff
	// TODO re-implement this later
	/*
    int i=0;
    int32_t *operandStack,*localVariables;

    if(frame == NULL)
        return ;

    DEBUG_LOG("          |----------|\n");
    localVariables = dj_frame_getLocalVariables(frame);
    for(i=dj_di_methodImplementation_getNrRefs(frame->method)-1;i>=0;i--)
    {
        DEBUG_LOG("%10p| %8d | local variable %d\n",&localVariables[i],localVariables[i],i);
    }

    DEBUG_LOG("          |----------|\n");
    operandStack = dj_frame_getStackStart(frame);
    for(i=dj_di_methodImplementation_getMaxStack(frame->method)-1;i>=0;i--)
    {
        DEBUG_LOG("%10p| %8d | operand %d\n",&operandStack[i],operandStack[i],i);
    }


    DEBUG_LOG("          |----------|\n");
    DEBUG_LOG("%10p|%4d  %4d| saved pc / saved nr_stack_elements\n",&(frame->pc),frame->nr_int_stack);
    DEBUG_LOG("%10p|%10p| infusion\n",&(frame->infusion),frame->infusion);
    DEBUG_LOG("%10p|%10d| method\n",&(frame->method),(uint32_t)frame->method);
    DEBUG_LOG("%10p|%10p| parent\n",frame,frame->parent);
    DEBUG_LOG("          |----------|\n");
    DEBUG_LOG("\n");

    dj_dump_stack(frame->parent);
    */
}



void dj_dump_int_array(dj_int_array *array)
{
    char type=0;
    switch(array->type)
    {
        case T_BOOLEAN: type='Z';break;
        case T_CHAR:    type='C';break;
        case T_FLOAT:   type='F';break;
        case T_DOUBLE:  type='D';break;
        case T_BYTE:    type='B';break;
        case T_SHORT:   type='S';break;
        case T_INT:     type='I';break;
        case T_LONG:    type='J';break;
        default:
            DEBUG_LOG("Unknown array component type: %d\n",array->type);
            DARJEELING_PRINTF("Unknown array component type: %d\n",array->type);
            dj_panic(DJ_PANIC_ILLEGAL_INTERNAL_STATE);
    }

    DEBUG_LOG("@%p{%d%c}\n",array,array->array.length,type);
}


#endif
