from flask import Flask, request, send_file
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

app = Flask(__name__)


def create_headers(element, headers):
    header_manager = ET.SubElement(element, "HeaderManager", {
        "guiclass": "HeaderPanel",
        "testclass": "HeaderManager",
        "testname": "HTTP Header Manager",
        "enabled": "true"
    })

    collection = ET.SubElement(header_manager, "collectionProp", {
        "name": "HeaderManager.headers"
    })

    for key, value in headers.items():
        header = ET.SubElement(collection, "elementProp", {
            "name": key,
            "elementType": "Header"
        })
        ET.SubElement(header, "stringProp", {"name": "Header.name"}).text = key
        ET.SubElement(header, "stringProp", {"name": "Header.value"}).text = value

    return header_manager


def create_sampler(parent, tc):
    parsed = urlparse(tc["url"])

    sampler = ET.SubElement(parent, "HTTPSamplerProxy", {
        "guiclass": "HttpTestSampleGui",
        "testclass": "HTTPSamplerProxy",
        "testname": tc["name"],
        "enabled": "true"
    })
