# Darjeeling Infusion Format

This documentation was created by looking at the source in DIVisitor.java

## AbstractReferencedInfusionList

~~~{.c}
uint8_t ElementId;

// Element List
uint8_t NumberOfElmenets;
// for each element
uint16_t Offset;
// for each element
char* InfusionName; // NULL terminated
~~~

## AbstractHeader

~~~{.c}

uint8_t AbstractHeaderId;
uint8_t MajorVersion;
uint8_t MinorVersion;
uint8_t EntryPointEntityId; // 255 if no entry point available
char* InfusionName;         // NULL terminated
~~~

## InternalClassDefinition

~~~{.c}
uint8_t ReferenceFieldCount;
uint8_t NonReferenceFieldsSize;
uint8_t SuperClassInfusionId;    // 255 darjeeling.Object
uint8_t SuperClassLocalId;       // 0   darjeeling.Object
uint8_t ClInitMethodId;          // 255 if none
uint8_t RootInfusionId;
uint8_t RootLocalId;

// Interface List
uint8_t NumberOfInterfaces;
// for each interface
uint8_t InterfaceXInfusionId;
uint8_t InterfaceXLocalId;

// Method Table
uint8_t NumberOfMethods;
// for each method
uint8_t MethodDefinitionInfusionId;
uint8_t MethodDefinitionLocalId;
uint8_t MethodImplementationInfusionId;
uint8_t MethodImplementationLocalId;
~~~


## InternalMethodImplementation

~~~{.c}
uint8_t ReferenceArgumentCount;
uint8_t IntegerArgumentCount;
uint8_t ReferenceLocalVariableCount;
uint8_t IntegerLocalVariableCount;
uint8_t TotalNumberOfParameters;  // including this
uint8_t MaxStack;
uint8_t Flags;                    // IsStatic, IsNative
uint8_t ReturnType

// Code
uint16_t CodeLengthInBytes;
uint8_t Code[CodeLengthInBytes];

// Exception Handler Table
uint8_t NumberOfExceptionHandler;
// for each exception handler
uint8_t CatchTypeInfusionId;
uint8_t CatchTypeLocalId;
uint16_t PcStart;
uint16_t PcEnd;
uint16_t HandlerPc;
~~~


## AbstractStaticFieldList

~~~{.c}
uint8_t ElementId;
uint8_t NumberOfReferences;
uint8_t NumberOfBytes;
uint8_t NumberOfShorts;
uint8_t NumberOfInts;
uint8_t NumberOfLongsl;
~~~


## InternalStringTable

~~~{.c}
uint8_t ElementId;
uint16_t NumberOfStrings;
// for each string
uint16_t Offset;  // relative to start of StringTable
// for each string
uint16_t Length;
uint8_t String[Length];	// NOT NULL terminated
~~~


