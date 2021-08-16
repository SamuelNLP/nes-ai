"""
Prerequisite functions to help and assert inputs and outputs condition and type
"""

from typing import Iterable, Optional, Type, TypeVar, Union, no_type_check

# create a type var to then tests if input type is the same as output type for example
TypeX = TypeVar("TypeX")
TypeY = TypeVar("TypeY", bound=Iterable)
TypeS = TypeVar("TypeS", bound=Iterable)


# conditions
def require(condition: bool, message: str = "Requirement failed!"):
    """
    Test one condition

    Parameters
    ----------
    condition : bool
        boolean condition
    message : str
        custom message to add to the assert

    """
    if not condition:
        raise ValueError(message)


def require_one_in_all(
    collection_conditions: Iterable[bool],
    message: str = "Not even one requirement met!",
):
    """
    Require one condition in a collection of conditions

    Parameters
    ----------
    collection_conditions : Iterable
        conditions to be tested
    message : str
        custom message to add to the assert

    """
    if not any(collection_conditions):
        raise ValueError(message)


def require_all_in_all(
    collection_conditions: Iterable[bool], message: str = "Not all requirements met!"
):
    """
    Require all conditions in a collection of conditions

    Parameters
    ----------
    collection_conditions : Iterable
        conditions to be tested
    message : str
        custom message to add to the assert

    """
    if not all(collection_conditions):
        raise ValueError(message)


# types
@no_type_check
def require_type(variable: TypeX, expected_type: Type) -> TypeX:
    """
    Require type of variable

    Parameters
    ----------
    variable : TypeX
        variable to be type tested
    expected_type : Type
        type to be expected

    Returns
    -------
    TypeX
        If assert is True, it returns the variable

    """
    if not isinstance(variable, expected_type):
        raise TypeError(f"Expected type {expected_type}, got {type(variable)}!")

    return variable


@no_type_check
def require_one_of_types(variable: TypeX, allowed_types: TypeY) -> TypeX:
    """
    Require one of the types specified

    Parameters
    ----------
    variable : TypeX
        variable to be type tested
    allowed_types : TypeY
        types allowed

    Returns
    -------
    TypeX
        If assert is True, it returns the variable

    """
    if not any(isinstance(variable, allowed_type) for allowed_type in allowed_types):
        raise TypeError(
            f"Expected one of {allowed_types} types in variable, got {type(variable)}!"
        )

    return variable


@no_type_check
def require_all_of_type(iterable: TypeY, expected_type: Type) -> TypeY:
    """
    Require all objects from an iterable to be of the type specified

    Parameters
    ----------
    iterable : TypeY
        iterable of objects to be type tested
    expected_type : Type
        type allowed

    Returns
    -------
    TypeY
        If assert is True, it returns the iterable passed

    """
    if not all(isinstance(variable, expected_type) for variable in iterable):
        raise TypeError(
            f"Expected all values in variable to be of type {expected_type}!"
        )

    return iterable


@no_type_check
def require_all_same_type(
    iterable: TypeY, allowed_types: Optional[TypeS] = None
) -> TypeS:
    """
    Require all objects from iterable to be of the same type

    Parameters
    ----------
    iterable : TypeY
        iterable of objects to be type tested
    allowed_types : TypeS, optional
        Types allowed

    Returns
    -------
    TypeS
        If assert is True, it returns the iterable passed

    """
    if len(set(map(type, iterable))) > 1:
        raise TypeError("All elements of iterable must be of the same type.")

    if allowed_types is not None:
        require_one_of_types(set(iterable).pop(), allowed_types)

    return iterable


@no_type_check
def require_type_or_none(variable: TypeX, expected_type: Type) -> Union[TypeX, None]:
    """
    Require a type or None

    Parameters
    ----------
    variable : TypeX
        variable to be type tested
    expected_type : Type
        type allowed apart from None

    Returns
    -------
    TypeS, optional
        If assert is True, it returns the iterable passed

    """
    if variable is None:
        return None
    return require_type(variable, expected_type)
