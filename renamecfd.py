#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# RENAMECFD - Renombra archivos de CFD
# Autor: Ricardo Torres
# email: rictor@cuhrt.com
# blog: htpp://rctorr.wordpress.com
# twitter: @rctorr
#
# Descripción
# Este script ayuda a leer un CFD para despues renombrar el archivo
# de la siguiente manera:
#    Fecha_RFCemisor_serie_folio_subtotal_iva_total.xml
#
# Fecha: Fecha en que se generó el comprobante
# RFCemisor: RFC de quien emite el cfd/cfdi
# Serie y Folio: Numero de Serie y folio de la factura
# Subtotal, iva, total: Importes de la factura.
#
# El nombre del xml se proporciona desde la línea de comandos, de tal forma que
# se puede usar en algún otro script para automatizar el proceso.
#
###############################################################################

# 17-01-2014
# - Ahora permite indicar archivos con algún path distinto a donde está el
#   script
#
# 16-01-2014
# - Se modifica para que pueda ser utilizado en batch y haceptar comodines
#   en el nombre de archivo
#
# Ver 1.1
# - Se corrige problema con los tags para cfdi
#
# Ver 1.0
# - Se lee el nombre del archivo desde la línea de comando
# - Se leer los atributos del archivo xml
# - Genera el nombre con la sintaxis solicitada
# - Renombra el archivo xml al nuevo nombre
#

import sys
import os
from optparse import OptionParser
from xml.dom import minidom


class XmlCFD(object):
    """
       Esta clase se encarga de realizar todas las operaciones relacionadas
       con la manipulación del archivo xml de facturación electrónica
    """
    nomFileXml = ''

    def __init__(self, nomFileXml):
        """ Initialize instance. """
        self.nomFileXml = nomFileXml
        self.atributos = dict()

    def getAtributos(self):
        """ Regresa los atributos necesario para formar el nombre del archivo. """

        if os.path.isfile(self.nomFileXml):
            xmlDoc = minidom.parse(self.nomFileXml)
            nodes = xmlDoc.childNodes
            comprobante = nodes[0]
            
            compAtrib = dict(comprobante.attributes.items())
            self.atributos['serie'] = compAtrib['serie']
            self.atributos['folio'] = compAtrib['folio']
            # Se trunca la parte de la hora de emisión
            self.atributos['fecha'] = compAtrib['fecha'][:10]
            self.atributos['total'] = compAtrib['total'].rjust(10,'0')
            self.atributos['subTotal'] = compAtrib['subTotal'].rjust(10,'0')
            version = compAtrib['version']

            if version == "1.0" or version == "2.0" or version == "2.2": # CFD
                emisor = comprobante.getElementsByTagName('Emisor')
                impuestos = comprobante.getElementsByTagName('Impuestos')
            elif version == "3.2" or version == "3.0": # CFDi
                emisor = comprobante.getElementsByTagName('cfdi:Emisor')
                impuestos = comprobante.getElementsByTagName('cfdi:Impuestos')
            else:
                print
                print "El archivo xml no es una versión válida de cfd!"
                print
                sys.exit(1)
                
            self.atributos['rfc'] = emisor[0].getAttribute('rfc')
            self.atributos['nombre'] = emisor[0].getAttribute('nombre')
            self.atributos['iva'] = impuestos[0].getAttribute('totalImpuestosTrasladados').rjust(10,'0')
        
        return self.atributos

    def rename(self, verbose):
        """ Renombra el archivo xml de la forma:
                Fecha_RFCemisor_serie_folio_subtotal_iva_total.xml
            
            Regresa el nuevo nombre del archivo
        """
        
        self.getAtributos()
        
        nomFileXmlNew = os.path.dirname(self.nomFileXml)
        nomFileXmlNew += os.sep if len(nomFileXmlNew) > 0 else ""
        nomFileXmlNew += self.atributos['fecha']
        nomFileXmlNew += '_'+self.atributos['rfc']
        nomFileXmlNew += '_'+self.atributos['serie']
        nomFileXmlNew += '_'+self.atributos['folio']
        nomFileXmlNew += '_'+self.atributos['subTotal']
        nomFileXmlNew += '_'+self.atributos['iva']
        nomFileXmlNew += '_'+self.atributos['total']
        nomFileXmlNew += '.xml'
            
        os.rename(self.nomFileXml, nomFileXmlNew)
        if verbose:
            print self.nomFileXml+" => "+nomFileXmlNew

        return nomFileXmlNew

def main(argv):

    usage = "%prog [opciones] archivocfd.xml|*.xml"
    add_help_option = False
    parser = OptionParser(usage=usage, add_help_option=add_help_option)
    parser.add_option("-h", "--help", action="help",
         help=u"muestra este mensaje de ayuda y termina")
    parser.add_option("-v", "--verbose", action="store_true",
         help=u"Va mostrando la lista de los archivos modificados")
    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        sys.exit(0)
    if options.verbose:
        verbose = True
    else:
        verbose = False

    for item in args:
        nomFileXml = item
        if not os.path.isfile(nomFileXml):
            print "El archivo "+nomFileXml+" no existe."
        else:
            xmlcfd = XmlCFD(nomFileXml)
            xmlcfd.rename(verbose)

if __name__ == "__main__":
  main(sys.argv[1:])
