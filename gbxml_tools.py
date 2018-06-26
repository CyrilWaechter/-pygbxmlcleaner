# coding: utf8
import xml.etree.ElementTree as ET


def gbxml_tag(tag):
    # type: (str) -> str
    gbxml_ns = r'{http://www.gbxml.org/schema}'
    return '{}{}'.format(gbxml_ns ,tag)


class Surface:
    def __init__(self, surface):
        self.surface = surface

    @property
    def id(self):
        return self.surface.get("id")

    @property
    def area(self):
        try:
            geom = self.surface.find('{http://www.gbxml.org/schema}RectangularGeometry')
            width = float(geom.find('{http://www.gbxml.org/schema}Width').text)
            height = float(geom.find('{http://www.gbxml.org/schema}Height').text)
            return width * height
        except AttributeError:
            return


def erase_small_surfaces(file, output_file=None, tolerance=1):
    """Remove small surfaces and space boundaries from a gbxml file"""
    if output_file is None:
        output_file = file.replace(".xml", "_optimized.xml")

    """ Necessary to not get a namespace prefix when writing output_file
    cf : https://stackoverflow.com/questions/8983041/saving-xml-files-using-elementtree"""
    ET.register_namespace('', "http://www.gbxml.org/schema")

    ns = {'gb':'http://www.gbxml.org/schema'}

    tree = ET.parse(file)

    root = tree.getroot()

    campus = root.find('gb:Campus', ns)

    # find and delete surface with an area inferior to tolerance
    deleted_surface_id = []
    for surface in campus.findall('gb:Surface',ns):
        surf_object = Surface(surface)
        area = surf_object.area
        if area and area < tolerance:
            deleted_surface_id.append(surf_object.id)
            campus.remove(surface)

    building = campus.find('gb:Building', ns)

    for space in building.findall('gb:Space', ns):
        for space_boundary in space.findall('gb:SpaceBoundary', ns):
            if space_boundary.get("surfaceIdRef") in deleted_surface_id:
                space.remove(space_boundary)

    tree.write(output_file)


if __name__ == '__main__':
    erase_small_surfaces("file.xml")
