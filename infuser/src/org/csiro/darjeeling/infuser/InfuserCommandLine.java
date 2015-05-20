/*
 * InfuserCommandLine.java
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

package org.csiro.darjeeling.infuser;

import java.io.FileNotFoundException;
import java.io.IOException;

import org.csiro.darjeeling.infuser.logging.Logging;

import com.beust.jcommander.JCommander;

public class InfuserCommandLine
{

	public static void printUsage()
	{
	}

	public static void main(String[] args)
	{
		Logging.instance.addVerbose(Logging.VerboseOutputType.ARGUMENTS_PARSING);

		InfuserArguments infuserArgs = new InfuserArguments();
		JCommander commander = new JCommander(infuserArgs);
		commander.setProgramName(Infuser.greeting);
		try {
			// parse arguments
			commander.parse(args);
			infuserArgs.checkInputFileExistance();

			// do infusion
			Infuser infuser = new Infuser(infuserArgs);
			infuser.process();
		} catch (com.beust.jcommander.ParameterException | FileNotFoundException ex)
		{
			System.out.println("error: " + ex.getMessage());
			commander.usage();
			System.exit(-1);
		}
		catch (InfuserException ex)
		{
			System.out.println(ex.getMessage());
			ex.printStackTrace();
			System.exit(-1);
		} catch (IOException ex) {
			System.out.println(ex.getMessage());
			ex.printStackTrace();
			System.exit(-1);
		}

	}

}
