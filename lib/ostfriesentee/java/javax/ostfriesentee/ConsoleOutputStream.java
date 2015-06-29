/*
 * ConsoleOutputStream.java
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

import java.io.OutputStream;

/**
 * @author Michael Maaser
 */
public class ConsoleOutputStream extends OutputStream {

	/* (non-Javadoc)
	 * @see java.io.OutputStream#write(int)
	 */
	public void write(int b) {
		Ostfriesentee.print(b);
	}

	public void write(byte[] b)
	{
		Ostfriesentee.print(b);
	}
}
