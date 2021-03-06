/*
 * Ostfriesentee.java
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

package javax.ostfriesentee;

import java.io.PrintStream;

/**
 * 
 * The Ostfriesentee class contains some general purpose methods such as printing to the default console, an assertion method for 
 * unit testing, and some other bits and pieces.
 * 
 * @author Niels Brouwers
 * @author Kevin Laeufer
 *
 */
public class Ostfriesentee
{
	static {
		System.out = new PrintStream(new ConsoleOutputStream());
	}

	private static native void _print(String string);
	private static native void _print(byte[] b);
	private static native void _print(int b);

	/**
	 * Prints a String to the default console.
	 * @param str string to print
	 */
	public static void print(String str)
	{
		if (str==null) throw new NullPointerException();
		_print(str);
	}

	/**
	 * Prints bytes to the default console.
	 * @param b bytes to print
	 */
	public static void print(byte[] b)
	{
		if (b==null) throw new NullPointerException();
		_print(b);
	}

	/**
	 * Prints bytesto the default console.
	 */
	public static void print(int b)
	{
		_print(b);
	}

	/**
	 * Assertion method for unit testing purposes. Prints the test nr and wether the test failed or passed.
	 * @param testNr test nr.
	 * @param success whether the test failed or passed, true being a pass.
	 */
	public static native void assertTrue(int testNr, boolean success);

	public static native void printTestResults();

	/**
	 * @return the amount of free memory, in bytes.
	 */
	public static native int getMemFree();
}
