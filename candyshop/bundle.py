from __future__ import print_function

import os
from ast import literal_eval

from lxml import etree

from .utils import find_files

MANIFEST_FILES = ['__odoo__.py', '__openerp__.py', '__terp__.py']


class ModuleProperties(object):
    def __init__(self, data):
        for key in data:
            setattr(self, key, data[key])


class Module(object):

    def __init__(self, bundle=None, path=None):
        assert os.path.isdir(path), \
            '%s is not a directory or does not exist.' % path
        assert (isinstance(bundle, ModulesBundle) or not bundle), \
            'Wrong bundle type.'

        self.bundle = bundle
        self.path = path
        self.manifest = self.get_manifest()

        assert self.manifest, \
            'The specified path does not contain a manifest file.'
        assert self.is_python_package(), \
            'The module is not a python package.'

        self.properties = ModuleProperties(self.extract_properties())
        self.properties.slug = os.path.basename(self.path)

    def extract_properties(self):
        try:
            with open(self.manifest) as properties:
                props = literal_eval(properties.read())
        except BaseException:
            raise IOError('An error ocurred while reading %s.' % self.manifest)
        else:
            return props

    def is_python_package(self):
        if find_files(self.path, '__init__.py'):
            return True
        return False

    def get_manifest(self):
        """return False if the path doesn't contain an odoo module, and the full
        path to the module manifest otherwise"""
        for mfst in MANIFEST_FILES:
            found = find_files(self.path, mfst)
            if found:
                return found[0]
        return False

    def get_record_ids_module_references(self):
        def generator(data):
            for xmldict in data:
                for ids in xmldict.values():
                    for id in ids:
                        yield id.split('.')[0]
        return list(set(generator(self.get_record_ids())))

    def get_record_ids(self):
        for data in self.properties.data:
            datafile = os.path.join(self.path, data)
            if os.path.splitext(datafile)[1].lower() == '.xml':
                yield {data: self.get_record_ids_fromfile(datafile)}

    def parse_xml_fromfile(self, xml_file):
        """Get xml parsed.
        :param xml_file: Path of file xml
        :return: Doc parsed (lxml.etree object)
            if there is syntax error return string error message
        """
        try:
            doc = etree.parse(open(xml_file))
        except etree.XMLSyntaxError as xmlsyntax_error_exception:
            return xmlsyntax_error_exception.message
        return doc

    def get_records_fromfile(self, xml_file, model=None):
        """Get tag `record` of a openerp xml file.
        :param xml_file: Path of file xml
        :param model: String with record model to filter.
                      if model is None then get all.
                      Default None.
        :return: List of lxml `record` nodes
            If there is syntax error return []
        """
        if model is None:
            model_filter = ''
        else:
            model_filter = "[@model='{model}']".format(model=model)
        doc = self.parse_xml_fromfile(xml_file)
        return doc.xpath("/openerp//record" + model_filter) + \
            doc.xpath("/odoo//record" + model_filter) \
            if not isinstance(doc, basestring) else []

    def get_record_ids_fromfile(self, xml_file, module=None):
        """Get xml ids from tags `record of a openerp xml file
        :param xml_file: Path of file xml
        :param model: String with record model to filter.
                      if model is None then get all.
                      Default None.
        :return: List of string with module.xml_id found
        """
        xml_ids = []
        for record in self.get_records_fromfile(xml_file):
            xml_module, xml_id = record.get('id').split('.') \
                if '.' in record.get('id') \
                else [self.properties.slug, record.get('id')]
            if module and xml_module != module:
                continue
            # Support case where using two xml_id:
            #  1) With noupdate="1"
            #  2) With noupdate="0"
            noupdate = "noupdate=" + record.getparent().get('noupdate', '0')
            xml_ids.append(
                xml_module + '.' + xml_id + '.' + noupdate)
        return xml_ids


class ModulesBundle(object):

    def __init__(self, path=None):
        assert os.path.isdir(path), \
            '%s is not a directory or does not exist.' % path

        self.path = path

        try:
            self.modules = list(self.get_modules())
        except BaseException:
            print('The specified path contains broken Odoo Modules.')
            raise
        else:
            assert self.modules, \
                'The specified path does not contain valid Odoo modules.'
            self.name = os.path.basename(self.path)
            self.oca_dependencies = self.parse_oca_dependencies()

    def get_modules(self):
        for mfst in MANIFEST_FILES:
            for mods in find_files(self.path, mfst):
                yield Module(self, os.path.dirname(mods))

    def get_oca_dependencies_file(self):
        oca_dependencies_file = os.path.join(self.path, 'oca_dependencies.txt')
        if os.path.isfile(oca_dependencies_file):
            self.oca_dependencies_file = oca_dependencies_file
            return True
        return False

    def parse_oca_dependencies(self):
        if self.get_oca_dependencies_file():
            with open(self.oca_dependencies_file) as oca:
                deps = [d.split() for d in oca.read().split('\n')]
            return {k: v for k, v in filter(None, deps)}
        return {}
