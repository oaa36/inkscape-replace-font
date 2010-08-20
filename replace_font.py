#!/usr/bin/env python 
'''
replace_font.py

Copyright (C) 2010 Craig Marshall, craig9 [at] gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA

-----------------------

This script finds all fonts in the current drawing that match the 
specified find font, and replaces it with the specified replacement
font.
'''

import os
import sys
import inkex
import simplestyle

tags_to_check = ['{http://www.w3.org/2000/svg}tspan',
							'{http://www.w3.org/2000/svg}text',
							'{http://www.w3.org/2000/svg}flowRoot',
							'{http://www.w3.org/2000/svg}flowPara',
							'{http://www.w3.org/2000/svg}flowSpan']
attributes_to_check = ['font-family', '-inkscape-font-specification']

class ReplaceFont(inkex.Effect):
	'''
	Replaces all instances of one font with another
	'''
	def __init__(self):
		inkex.Effect.__init__(self)	
		self.OptionParser.add_option("--find", action="store", 
										type="string", dest="find",
										default=None, help="")
										
		self.OptionParser.add_option("--replace", action="store", 
										type="string", dest="replace", 
										default=None, help="")
		
		self.OptionParser.add_option("--selected_only", action="store", 
										type="inkbool", dest="selected_only", 
										default=None, help="")

		self.OptionParser.add_option("--every", action="store", 
										type="inkbool", dest="every", 
										default=None, help="")

		self.OptionParser.add_option("--list_all", action="store", 
										type="inkbool", dest="list_all", 
										default=None, help="")
		self.selected_items = []

	def report_replacements(self, num):
		if num == 0:
			inkex.errormsg('Couldn\'t find anything using that font, please ensure the spelling and spacing is correct.')
			sys.exit(0)
		else:
			if num > 1:
				occurrences = "occurrences"
			else:
				occurrences = "occurrence"
			inkex.errormsg("Successfully replaced %d %s of that font" % (num, occurrences))

	def report_findings(self, findings):
		if len(findings) == 0:
			inkex.errormsg('Couldn\'t find a single font in this document/selection.')
		else:
			if len(findings) == 1:
				inkex.errormsg("Found the following font only: %s" % findings[0])
			else:
				inkex.errormsg("Found the following fonts:\n%s" % '\n'.join(findings))

	def find_child_text_items(self, node):
		if node.tag in tags_to_check:
			self.selected_items.append(node)
			for child in node:
				self.find_child_text_items(child)

	def relevant_items(self):
		if self.options.selected_only:
			self.selected_items = []
			for item in self.selected.iteritems():
				self.find_child_text_items(item[1])
			return self.selected_items
		else:
			return self.document.getroot().getiterator()

	def find_replace(self):
		replacements_made = 0
		for el in self.relevant_items():
			if el.tag in tags_to_check and 'style' in el.attrib:		
				replaced = False
				style_dict = simplestyle.parseStyle(el.attrib['style'])
				for att in attributes_to_check:
					if att in style_dict and (style_dict[att].strip().lower() == self.options.find or self.options.every):
						style_dict[att] = self.options.replace
						el.attrib['style'] = simplestyle.formatStyle(style_dict)
						replaced = True
				if replaced:
					replacements_made += 1
		self.report_replacements(replacements_made)

	def list_all(self):
		fonts_found = []
		for el in self.relevant_items():
			if el.tag in tags_to_check and 'style' in el.attrib:
				style_dict = simplestyle.parseStyle(el.attrib['style'])
				for att in attributes_to_check:
					if att in style_dict:
						new_font = style_dict[att]
						if not new_font in fonts_found:
							fonts_found.append(new_font)
		self.report_findings(fonts_found)

	def effect(self):
		if self.options.list_all:
			self.list_all()
			sys.exit(0)
		else:
			self.options.find = self.options.find.strip().lower()
			self.find_replace()

if __name__ == "__main__":
	e = ReplaceFont()
	e.affect()

