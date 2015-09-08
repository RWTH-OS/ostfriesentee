/*
 * CHeaderVisitor.java
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of Ostfriesentee.
 *
 * Ostfriesentee is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ostfriesentee is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with Ostfriesentee.  If not, see <http://www.gnu.org/licenses/>.
 */

package org.csiro.darjeeling.infuser.outputphase;

import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;

import org.apache.bcel.generic.Type;
import org.csiro.darjeeling.infuser.structure.BaseType;
import org.csiro.darjeeling.infuser.structure.DescendingVisitor;
import org.csiro.darjeeling.infuser.structure.Element;
import org.csiro.darjeeling.infuser.structure.ParentElement;
import org.csiro.darjeeling.infuser.structure.elements.AbstractField;
import org.csiro.darjeeling.infuser.structure.elements.AbstractHeader;
import org.csiro.darjeeling.infuser.structure.elements.AbstractMethod;
import org.csiro.darjeeling.infuser.structure.elements.AbstractMethodDefinition;
import org.csiro.darjeeling.infuser.structure.elements.AbstractMethodImplementation;
import org.csiro.darjeeling.infuser.structure.elements.internal.InternalClassDefinition;
import org.csiro.darjeeling.infuser.structure.elements.internal.InternalClassList;
import org.csiro.darjeeling.infuser.structure.elements.internal.InternalInfusion;
import org.csiro.darjeeling.infuser.structure.elements.internal.InternalMethodDefinition;
import org.csiro.darjeeling.infuser.structure.elements.internal.InternalMethodDefinitionList;

/**
 *
 * Outputs a C++ header file.
 *
 * @author Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 */
public class CPPWrapperVisitor extends DescendingVisitor
{

	private PrintWriter writer;
	private String infusionName;

	public CPPWrapperVisitor(PrintWriter writer)
	{
		this.writer = writer;
	}

	@Override
	public void visit(InternalInfusion element)
	{
		AbstractHeader header = element.getHeader();
		infusionName = header.getInfusionName().replace("-", "_");

		writer.printf("#ifndef JLIB_%s_HPP\n", infusionName.toUpperCase());
		writer.printf("#define JLIB_%s_HPP\n", infusionName.toUpperCase());
		writer.println("");

		writer.println("/**");
		writer.println(" * This file is machine-generated by the infuser tool.");
		writer.println(" * Do not edit.");
		writer.println(" */");

		writer.println("");
		writer.println("#include <hpp/ostfriesentee.hpp>");
		writer.println("// include C header for structs");
		writer.printf("#include <jlib_%s.h>\n", header.getInfusionName());
		writer.println("");

		visit((ParentElement<Element>)element);

		writer.println("");
		writer.printf("#endif // JLIB_%s_HPP\n", infusionName.toUpperCase());
	}

	public void visit(InternalClassList element)
	{
		super.visit(element);
		writer.println("");
	}

	public void visit(InternalClassDefinition element)
	{
		// name of the struct from the c header file
		String structName = "_" + infusionName.toUpperCase() + "_STRUCT_" +
				element.getName().replaceAll("\\.", "_").replaceAll("\\$", "_inner_");
		String[] nameParts = element.getName().split("\\.");
		String className = nameParts[nameParts.length - 1];

		// print namespaces
		for(int ii = 0; ii < nameParts.length - 1; ii++) {
			writer.printf("namespace %s {\n", nameParts[ii]);
		}

		writer.printf("class %s : public ostfriesentee::Object {\n", className);
		writer.printf("\tstatic constexpr uint8_t ClassId = %d;\n",
				element.getGlobalId().getEntityId());

		writer.println("\npublic:");
		writer.printf("\t%s(const %s&) = delete;\n", className, className);
		writer.printf("\t%s& operator=(const %s&) = delete;\n", className, className);
		writer.println("\npublic:");

		// generate constructor
		AbstractMethod ctor = null;
		for(AbstractMethod method : element.getChildren()) {
			if(method.getMethodDef().getName().equals("<init>")) {
				ctor = method;
				break;
			}
		}
		if(ctor != null) {
			writeMethodIds("constructor", ctor);
			String args = createArgList(ctor.getMethodImpl());
			if(args.length() > 0) {
				writer.printf("\t%s(ostfriesentee::Infusion& infusion, %s) :\n", className, args);
			} else {
				writer.printf("\t%s(ostfriesentee::Infusion& infusion) :\n", className);
			}
			writer.println("\t\t\tostfriesentee::Object(infusion) {");

			writer.printf("\t\tthis->obj = create(this->infusion, ClassId);\n");
			writer.println("\t\tdj_mem_addSafePointer((void**)&this->obj);\n");

			writeCodeToCallMethod("constructor", ctor.getMethodImpl());

			writer.println("\n\t}");
		} else {
			;	// TODO: when can this happen?
		}

		// destructor
		writer.printf("\t~%s() {\n", className);
		writer.println("\t\tdj_mem_removeSafePointer((void**)&this->obj);");
		writer.println("\t}\n");

		// getUnderlying
		writer.printf("\t%s* getUnderlying() {\n", structName);
		writer.printf("\t\treturn (%s*)(this->obj);\n", structName);
		writer.println("\t}\n");

		// methods
		HashMap<String, Integer> methodNames = new HashMap<String, Integer>();
		for(AbstractMethod method : element.getChildren()) {
			String name = method.getMethodDef().getName();
			if(name.equals("<init>")) {
				continue;
			}

			// check for array arguments as we do not support these
			boolean hasArrayArgument = false;
			for(Type type : Type.getArgumentTypes(method.getMethodDef().getSignature())) {
				if(type.toString().endsWith("[]")) {
					hasArrayArgument = true;
					break;
				}
			}

			// check for C++ keywords that are not keywords in java
			if(name.equals("delete")) {
				name = name + "X";
			}

			// make sure we do not have duplicate names
			if(!methodNames.containsKey(name)) {
				methodNames.put(name, 1);
			} else {
				int number = methodNames.get(name);
				methodNames.replace(name, number + 1);
				name = name + number;
			}

			writeMethodIds(name, method);

			if(hasArrayArgument) {
				writer.printf("\t// The `%s` method is missing", name);
				writer.println(" because it takes an array as argument.");
				writer.print("\t// Array parameters are currently not supported");
				writer.println(" in the c++ wrapper.\n");
			} else {
				String args = createArgList(method.getMethodImpl());
				String ret = getCType(method.getMethodDef().getReturnType());
				writer.printf("\t%s %s(%s) {\n", ret, name, args);
				writeCodeToCallMethod(name, method.getMethodImpl());
				writer.println("\t}\n");
			}
		}

		// end class
		writer.printf("}; // class %s\n\n", className);

		// end namespaces
		for(int ii = 0; ii < nameParts.length - 1; ii++) {
			writer.printf("} // namespace %s\n", nameParts[ii]);
		}
		writer.println("\n");
	}

	private String createArgList(AbstractMethodImplementation method) {
		Type argTypes[] = Type.getArgumentTypes(method.getMethodDefinition().getSignature());
		String args = "";
		int argCount = 0;
		for(Type arg : argTypes) {
			args += getCType(arg) + " arg" + argCount + ", "; argCount++;
		}
		if(args.length() >= 2) {
			return args.substring(0, args.length() - 2);
		} else {
			return "";
		}
	}

	private void writeCodeToCallMethod(String name, AbstractMethodImplementation method) {
		if(method.getIntegerArgumentCount() > 0) {
			writer.printf("\t\tint16_t intParams[%d];\n", method.getIntegerArgumentCount());
		}
		// reference parameters (+1 because of the this parameter)
		writer.printf("\t\tref_t refParams[%d];\n", method.getReferenceArgumentCount() + 1);
		writer.println("\t\tsetParam(refParams, 0, this->obj);");
		// iterate over arguments and write them to the stack variables
		Type argTypes[] = Type.getArgumentTypes(method.getMethodDefinition().getSignature());
		int argCount = 0;
		int intCount = 0;
		int refCount = 1;
		for(Type arg : argTypes) {
			writer.print("\t\tsetParam(");
			if(BaseType.fromBCELType(arg) == BaseType.Ref) {
				writer.printf("refParams, " + refCount + ", ");
				refCount++;
			} else {
				writer.printf("intParams, " + intCount + ", ");
				intCount += getWidth(arg);
			}
			writer.println("arg" + argCount + ");");
			argCount++;
		}
		writer.printf("\n\t\tthis->runMethod(%sImplementationId, refParams",
				name);
		if(method.getIntegerArgumentCount() > 0) {
			writer.println(", intParams);");
		} else {
			writer.println(");");
		}
	}

	private void writeMethodIds(String name, AbstractMethod element) {
		writer.print("\t// global definition id from infusion: ");
		writer.print(element.getMethodDef().getGlobalId().getInfusion());
		writer.print("\n\tstatic constexpr uint8_t ");
		writer.print(name);
		writer.print("DefinitionId = ");
		writer.print(element.getMethodDef().getGlobalId().getEntityId());
		writer.print(";\n");

		writer.print("\t// global implementation id from infusion: ");
		writer.print(element.getMethodImpl().getGlobalId().getInfusion());
		writer.print("\n\tstatic constexpr uint8_t ");
		writer.print(name);
		writer.print("ImplementationId = ");
		writer.print(element.getMethodImpl().getGlobalId().getEntityId());
		writer.print(";\n");
	}

	public void visit(InternalMethodDefinitionList element)
	{
		writer.println("// Method definitions");
		super.visit(element);
		writer.println("");
	}

	@Override
	public void visit(Element element)
	{
	}

	private String getCType(Type type) {
		return getCType(BaseType.fromBCELType(type));
	}
	private String getCType(BaseType type) {
		switch (type)
		{
		case Char:
			return "char";
		case Byte:
		case Boolean:
			return "int8_t";
		case Short:
			return "int16_t";
		case Int:
			return "int32_t";
		case Long:
			return "int64_t";
		case Ref:
			return "ref_t";
		case Void:
			return "void";
		default:
			return "";
		}
	}

	private int getWidth(Type type) {
		return getWidth(BaseType.fromBCELType(type));
	}

	/// width in multiples of 16bit
	private int getWidth(BaseType type) {
		switch (type)
		{
		case Char:
			return 1;
		case Byte:
		case Boolean:
			return 1;
		case Short:
			return 1;
		case Int:
			return 2;
		case Long:
			return 4;
		case Ref:
			return 1;
		default:
			return 0;
		}
	}
}
