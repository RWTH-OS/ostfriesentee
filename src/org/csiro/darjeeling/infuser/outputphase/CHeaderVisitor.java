/*
 * CHeaderVisitor.java
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
 
package org.csiro.darjeeling.infuser.outputphase;

import java.io.PrintWriter;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

import org.apache.bcel.generic.Type;
import org.csiro.darjeeling.infuser.structure.DescendingVisitor;
import org.csiro.darjeeling.infuser.structure.Element;
import org.csiro.darjeeling.infuser.structure.ParentElement;
import org.csiro.darjeeling.infuser.structure.elements.AbstractField;
import org.csiro.darjeeling.infuser.structure.elements.AbstractHeader;
import org.csiro.darjeeling.infuser.structure.elements.internal.InternalClassDefinition;
import org.csiro.darjeeling.infuser.structure.elements.internal.InternalClassList;
import org.csiro.darjeeling.infuser.structure.elements.internal.InternalInfusion;
import org.csiro.darjeeling.infuser.structure.elements.internal.InternalMethodDefinition;
import org.csiro.darjeeling.infuser.structure.elements.internal.InternalMethodDefinitionList;

/**
 * 
 * Outputs a C header file with #define statements linking human readable names such as 'BASE_CDEF_java_lang_Object' with generated entity IDs.
 * 
 * @author Niels Brouwers
 *
 */
public class CHeaderVisitor extends DescendingVisitor
{
	
	private PrintWriter writer;
	private String infusionName;
	
	public CHeaderVisitor(PrintWriter writer)
	{
		this.writer = writer;
	}
	
	@Override
	public void visit(InternalInfusion element)
	{
		AbstractHeader header = element.getHeader();
		infusionName = header.getInfusionName();
		
		writer.printf("#ifndef __%s_definitions_h\n", infusionName);
		writer.printf("#define __%s_definitions_h\n", infusionName);
		writer.println("");

		writer.println("/*");
		writer.println(" * This file is machine-generated by the infuser tool.");
		writer.println(" * Do not edit.");
		writer.println(" */");

		writer.println("");
		writer.println("#include <stdint.h>");
		writer.println("#include <pointerwidth.h> // for ref_t");
		writer.println("");
		writer.println(String.format("void %s_native_handler(uint8_t id);", header.getInfusionName()));
		writer.println("");
		
		visit((ParentElement<Element>)element);

		writer.println("");
		writer.println("#endif");
		writer.println("");
	}
	
	public void visit(InternalClassList element)
	{
		writer.println("// Class definitions");
		super.visit(element);
		writer.println("");
	}
	
	public void visit(InternalClassDefinition element)
	{
		String className = element.getName().replaceAll("\\.", "_").replaceAll("\\$", "_inner_");

		writer.printf("// %s\n", element.getName()); 

		writer.printf("#define %s_CDEF_%s %d\n",
				infusionName.toUpperCase(),
				className,
				element.getGlobalId().getEntityId()
				);
		
		// Get field list and sort it by offset
		List<AbstractField> fields = element.getFieldList().getFields();
		Collections.sort(fields, new Comparator<AbstractField>() {
			public int compare(AbstractField arg0, AbstractField arg1)
			{
				if (!arg0.isRef()&&arg1.isRef()) return -1;
				if (arg0.isRef()&&!arg1.isRef()) return 1;
				
				return arg0.getOffset() < arg1.getOffset() ? -1 : 1;
			}
		});
		
		writer.printf("typedef struct _%s_STRUCT_%s {\n", infusionName.toUpperCase(), className);
		for (AbstractField field : fields)
		{
			String typeString = "";
			switch (field.classify())
			{
				case Char:
					typeString = "char";
					break;
				case Byte:
				case Boolean:
					typeString = "int8_t";
					break;
				case Short:
					typeString = "int16_t";
					break;
				case Int:
					typeString = "int32_t";
					break;
				case Long:
					typeString = "int64_t";
					break;
				case Ref:
					typeString = "ref_t";
					break;
			}
			
			writer.printf("\t%s %s;\n", typeString, field.getName().replaceAll("\\$", "_"));
		}
		writer.printf("} __attribute__ ((__packed__)) %s_STRUCT_%s;\n\n", infusionName.toUpperCase(), className);
	}

	public void visit(InternalMethodDefinitionList element)
	{
		writer.println("// Method definitions");
		super.visit(element);
		writer.println("");
	}
	
	public void visit(InternalMethodDefinition element)
	{
		Type returnType = Type.getReturnType(element.getSignature());
		Type argTypes[] = Type.getArgumentTypes(element.getSignature());
		String descr = returnType + "_" + element.getName();
		for (Type argType : argTypes) descr += "_" + argType.toString();
		descr = descr.toString().replaceAll("\\p{Punct}", "_");
		
		writer.printf("#define %s_MDEF_%s %d\n",
				infusionName.toUpperCase(),
				descr,
				element.getGlobalId().getEntityId()
				);
	}

	@Override
	public void visit(Element element)
	{
	}

}
