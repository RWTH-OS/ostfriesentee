/*
 * InfuserArguments.java
 *
 * Copyright (c) 2008-2010 CSIRO, Delft University of Technology.
 * Copyright (c) 2015, Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
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


package org.csiro.darjeeling.infuser;
import static org.csiro.darjeeling.infuser.logging.Logging.VerboseOutputType.ARGUMENTS_PARSING;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.apache.bcel.classfile.ClassParser;
import org.apache.bcel.classfile.JavaClass;
import org.csiro.darjeeling.infuser.logging.Logging;
import org.csiro.darjeeling.infuser.structure.elements.external.ExternalInfusion;
import org.csiro.darjeeling.infuser.structure.elements.internal.InternalHeader;
import org.csiro.darjeeling.infuser.structure.elements.internal.InternalInfusion;
import org.w3c.dom.Document;
import org.xml.sax.SAXException;

import com.beust.jcommander.Parameter;


/**
 * Set of arguments and switches for the Infuser class.
 *
 *
 * @author Niels Brouwers
 * @author Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 */
public class InfuserArguments
{

	@Parameter(description = "Source (*.class) and header (*.dih) files.")
	private ArrayList<String> inputFiles = new ArrayList<String>();

	@Parameter(names = { "-n", "--name" }, description = "Name of the infusion")
	private String infusionName;

	@Parameter(names = { "-o", "--output" }, description = "The infusion output file.")
	private String infusionOutputFile;

	@Parameter(names = { "-h", "--header-output" }, description = "The infusion header output file.")
	private String headerOutputFile;

	@Parameter(names = { "-d", "--c-header-output" }, description = "The c header output file.")
	private String cHeaderOutputFile;

	@Parameter(names = { "-c", "--c-code-output" }, description = "The c code output file.")
	private String cCodeOutputFile;

	@Parameter(names = { "-r", "--rust-output" }, description = "The rust binding file.")
	private String rustOutputFile;

	// Internally used debug output file.
	private String debugOutputFile;

	/**
	 *  Creates a new, empty InfuserArguments instance. Can be used to programmatically drive
	 *  the infuser rather than through command line arguments.
	 */
	public InfuserArguments(){}

	/**
	 * Evaluates if all input files exist, throws a FileNotFoundException if this is not the case.
	 */
	public void checkInputFileExistance() throws FileNotFoundException {
		for(String fileName : inputFiles) {
			if(!fileExists(fileName)) {
				throw new FileNotFoundException("Input file " + fileName + " does not exist");
			}
		}
	}

	// Convenience method
	private static boolean fileExists(String name)
	{
		File file = new File(name);
		return file.exists();
	}


	/**
	 * Creates a new InternalInfusion object from the parameters in this class. It creates a header
	 * with the given name and version, parses and adds all the class files and header files.
	 * The resulting Infusion object is then ready for further processing.
	 * @return a new InternalInfusion instance with classes and headers loaded
	 * @throws InfuserException
	 * @throws IOException
	 */
	public InternalInfusion createInfusion(int majorVersion, int minorVersion) throws InfuserException, IOException
	{
		// create an infusion and create the header
		InternalHeader header = new InternalHeader(infusionName, majorVersion, minorVersion);
		InternalInfusion infusion = new InternalInfusion(header);

		// add header files
		for (String headerFileName : inputFiles)
		{
			if(!headerFileName.endsWith(".dih")) {	// if this is not a header file
				continue;
			}
			Logging.instance.printlnVerbose(ARGUMENTS_PARSING, String.format("Loading header file %s", headerFileName));
			if (!fileExists(headerFileName))
			{
				throw new InfuserException(String.format("File %s does not exist", headerFileName));
			} else
			{
				try {
					DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
					DocumentBuilder db = dbf.newDocumentBuilder();
					Document dom = db.parse(headerFileName);
					ExternalInfusion headerInfusion = ExternalInfusion.fromDocument(dom, headerFileName);
					infusion.addInfusion(headerInfusion);
				} catch(SAXException ex)
				{
					throw new InfuserException(String.format("Unable to parse class file %s", headerFileName), ex);
				} catch (ParserConfigurationException ex)
				{
					throw new InfuserException(String.format("Unable to parse class file %s", headerFileName), ex);
				} catch (IOException ex)
				{
					throw new InfuserException(String.format("Unable to parse class file %s", headerFileName), ex);
				}
			}
		}

		// add class files
		for (String fileName : inputFiles)
		{
			Logging.instance.printlnVerbose(ARGUMENTS_PARSING, String.format("Loading jar file %s", fileName));
			if(fileName.endsWith(".jar")) {
				JarFile jarFile = new JarFile(fileName);
				Enumeration<JarEntry> entries = jarFile.entries();
				while(entries.hasMoreElements()) {
					JarEntry entry = entries.nextElement();
					if(entry.getName().endsWith(".class")) {
						Logging.instance.printlnVerbose(ARGUMENTS_PARSING, String.format("Loading class %s", entry.getName()));
						ClassParser parser = new ClassParser(fileName, entry.getName());
						JavaClass javaClass = parser.parse();
						infusion.addJavaClass(javaClass);
					}
				}
				jarFile.close();
			} else if (fileName.endsWith(".class")) {
				Logging.instance.printlnVerbose(ARGUMENTS_PARSING, String.format("Loading class file %s", fileName));
				if (!fileExists(fileName))
				{
					throw new InfuserException(String.format("File %s does not exist", fileName));
				} else
				{
					try {
						ClassParser parser = new ClassParser(fileName);
						JavaClass javaClass = parser.parse();
						infusion.addJavaClass(javaClass);
					} catch (IOException ex)
					{
						throw new InfuserException(String.format("Unable to parse class file %s", fileName), ex);
					}
				}
			}
		}

		return infusion;
	}

	/**
	 * @return the infusionName
	 */
	public String getInfusionName()
	{
		return infusionName;
	}

	public String getInfusionOutputFile()
	{
		return infusionOutputFile;
	}

	public String getHeaderOutputFile()
	{
		return headerOutputFile;
	}

	public String getDefinitionOutputFile()
	{
		return cHeaderOutputFile;
	}

	public void setInfusionOutputFile(String infusionOutputFile)
	{
		this.infusionOutputFile = infusionOutputFile;
	}

	public void setHeaderOutputFile(String headerOutputFile)
	{
		this.headerOutputFile = headerOutputFile;
	}

	public void setDefinitionOutputFile(String definitionOutputFile)
	{
		this.cHeaderOutputFile = definitionOutputFile;
	}

	public void setInfusionName(String infusionName)
	{
		this.infusionName = infusionName;
	}

	public void setNativeOutputFile(String nativeOutputFile)
	{
		this.cCodeOutputFile = nativeOutputFile;
	}

	public String getNativeOutputFile()
	{
		return cCodeOutputFile;
	}

	public void setDebugOutputFile(String debugOutputFile)
	{
		this.debugOutputFile = debugOutputFile;
	}

	public String getDebugOutputFile()
	{
		return debugOutputFile;
	}

	public String getRustOutputFile() {
		return rustOutputFile;
	}

}
