from lxml import etree
from tqdm import tqdm
import argparse

if __name__ == "__main__":
    # Parses the arguments for input file and destination.
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str,
                        help='name of input filename')
    parser.add_argument('dest', type=str,
                        help='name of destination filename')
    parser.add_argument('ns', type=str,
                        help='Namespace to preserve in output')
    args = parser.parse_args()

    print("Reading MediaWiki XML file.")
    # Reads the MediaWiki file, and gets the root node.
    parsed = etree.parse(args.input)
    tree = parsed.getroot()

    print("Cleaning up tags.")
    # tqdm adds a progress bar. Useful for such a long operation.
    # Clean up the tags
    for elem in tqdm(tree.iterdescendants()):
        elem.tag = etree.QName(elem).localname

    print("Stripping namespace definition")
    # Here, we strip all the namespace definitions. We have no need for this.
    namespaces = tree.xpath('siteinfo/namespaces')
    for elem in tqdm(namespaces):
        elem.getparent().remove(elem)

    print("Removing pages in namespaces other than {0}".format(args.ns))
    ns = tree.xpath('page/ns')
    for elem in tqdm(ns):
        if elem.text != None and elem.text != args.ns:
            page = elem.getparent()
            page.getparent().remove(page)

    # Finds all pages with redirects, and removes them all.
    print("Removing pages with redirects")
    redirect = tree.xpath('page/redirect')
    for elem in tqdm(redirect):
        page = elem.getparent()
        page.getparent().remove(page)

    # Finds all the text element, and if the page is simply a disambigation page,
    # removes them.
    print("Removes all disambiguation pages")
    for elem in tqdm(tree.iterfind('.//%s' % "text")):
        if elem.text != None and "{{disambig}}" in elem.text.lower():
            page = elem.getparent().getparent()
            page.getparent().remove(page)

    # Finds these specific tags, and removes them. 
    # In-precise, but good enough.
    remove_elements = ["contributor", "comment", "parentid",
                       "model", "format", "timestamp", "minor", "ns"]
    print("Cleaning up unneeded information")
    for remove in tqdm(remove_elements):
        for subelem in tree.iterfind('.//%s' % remove):
            subelem.getparent().remove(subelem)

    print("Writing cleaned XML file.")
    etree.cleanup_namespaces(tree)
    with open(args.dest, "wb") as openFile:
        openFile.write(etree.tostring(tree, pretty_print=True))
