from rdf.blanknode import BlankNode
from rdf.uri import URI
from rdf.literal import Literal, PlainLiteral, TypedLiteral, is_well_typed_xml
from rdf.namespace import RDF, XSD


class TypeDescriptor:
    def __init__(self, type):
        self.type = type

class BlankNodeDescriptor(TypeDescriptor):
    def __call__(self, obj, context):
        return context.allocate(obj)

class Type:
    def __init__(self, class_set):
        if isinstance(class_set, type):
            class_set = (class_set,)
        self.class_set = frozenset(class_set)
        self.blank_node = self.nnn = BlankNodeDescriptor(self)

    def __contains__(self, obj):
        return isinstance(obj, tuple(self.class_set))

    def __lt__(self, other):
        return hash(self) < hash(other)

    def __gt__(self, other):
        return hash(self) > hash(other)

class ContainerMembershipPropertyType(Type):
    def __init__(self):
        super().__init__(URI)

    def __contains__(self, obj):
        if super().__contains__(obj):
            head, sep, tail = obj.rpartition('_')
            return head == RDF and tail.isdigit()
        else:
            return False

class DatatypeDescriptor(TypeDescriptor):
    def __call__(self, obj, context):
        return obj.datatype

class LiteralDescriptor(TypeDescriptor):
    def __init__(self, type, datatype=None):
        super().__init__(type)
        self.datatype = datatype

    def __call__(self, obj, context):
        if self.datatype is None:
            return PlainLiteral(obj.lexical_form)
        else:
            return TypedLiteral(obj.lexical_form, self.datatype)

class TypedLiteralType(Type):
    def __init__(self, datatype=None):
        super().__init__(TypedLiteral)
        if datatype is None:
            datatype = ()
        elif isinstance(datatype, str):
            datatype = {datatype}
        self.datatype_set = set(datatype)
        self.datatype = self.ddd = DatatypeDescriptor(self)

    def __contains__(self, obj):
        return (super().__contains__(obj) and
                (not self.datatype_set or obj.datatype in self.datatype_set))

    def literal(self, datatype=None):
        return LiteralDescriptor(self, datatype)

    sss = literal

class PlainLiteralType(Type):
    def __init__(self):
        super().__init__(PlainLiteral)

    def literal(self, datatype=None):
        return LiteralDescriptor(self, datatype)

    sss = literal

class WellTypedXMLLiteralType(Type):
    def __init__(self):
        super().__init__(Literal)

    def __contains__(self, obj):
        return super().__contains__(obj) and is_well_typed_xml(obj)

aaa = Type(URI)
bbb = Type(URI)
ddd = Type(URI)
eee = Type(URI)
uuu = Type({URI, BlankNode})
vvv = Type({URI, BlankNode})
xxx = Type({URI, BlankNode, Literal})
yyy = Type({URI, BlankNode, Literal})
lll = Type(Literal)
llp = PlainLiteralType()
llt = TypedLiteralType()
lls = TypedLiteralType(XSD.string)
llx = WellTypedXMLLiteralType()
cmp = ContainerMembershipPropertyType()

