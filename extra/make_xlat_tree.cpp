/*
 * This program generates the xlat_tree.py Python module
 * for use by anglicize.py.
 */

#include <map>
#include <string>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>

#include <map>

// UTF-8 char to roman representation correspondence.
struct XLatEntry
{
	const char* from;
	const char* to;
};

// Load input data.
#include "xlat_entries.h"

#define NUMBER_OF_ENTRIES (sizeof(xlat_entries) / sizeof(*xlat_entries))

#define XLAT_TREE_BEGIN "\n    XLAT_TREE: Dict[int, Any] = "
#define XLAT_TREE_END "\n    }"

struct XLatTreeNode;

// NodeMap matches the xlat_tree structure in the resulting
// xlat_tree.py Python module.
typedef std::map<char, XLatTreeNode*> NodeMap;

struct XLatTreeNode
{
	const char* encoded;
	NodeMap children;

	XLatTreeNode(const char* encoded) : encoded(encoded)
	{
	}
};

// This class builds a tree out of byte sequences of
// the input UTF-8 characters.
class XLatTreeGenerator
{
public:
	void AddXLatEntry(const XLatEntry* xlat_entry);
	std::string GenerateXLatTree() const;

private:
	static void PrintIndent(int indent, std::ostream& os);
	static void PrintTreeNode(std::ostream& os,
		const NodeMap* tree_node, int indent);

	NodeMap xlat_tree_root;
};

// This is the main procedure.
void XLatTreeGenerator::AddXLatEntry(const XLatEntry* xlat_entry)
{
	const char* ch = xlat_entry->from;
	NodeMap* tree_node = &xlat_tree_root;

	// Create nodes in the output tree for all but one
	// bytes in the input UTF-8 character.
	while (ch[1] != '\0')
	{
		std::pair<NodeMap::iterator, bool> insertion =
				tree_node->insert(
						NodeMap::value_type(*ch, NULL));
		if (insertion.second)
			insertion.first->second = new XLatTreeNode(NULL);
		tree_node = &insertion.first->second->children;
		++ch;
	}

	// Mark the node of the last byte as "finite" by assigning the
	// transliteration of the UTF-character to it.
	std::pair<NodeMap::iterator, bool> insertion =
			tree_node->insert(NodeMap::value_type(*ch, NULL));
	if (insertion.second)
		insertion.first->second = new XLatTreeNode(xlat_entry->to);
	else
		insertion.first->second->encoded = xlat_entry->to;
}

std::string XLatTreeGenerator::GenerateXLatTree() const
{
	std::stringstream ss;

	ss << XLAT_TREE_BEGIN;
	PrintTreeNode(ss, &xlat_tree_root, 1);

	return ss.str();
}

void XLatTreeGenerator::PrintIndent(int indent, std::ostream& os)
{
	while (--indent >= 0)
		os << "    ";
}

void XLatTreeGenerator::PrintTreeNode(
	std::ostream& os, const NodeMap* tree_node, int indent)
{
	os << "{\n";
	NodeMap::const_iterator it = tree_node->begin();
	for (;;)
	{
		PrintIndent(indent + 1, os);
		os << "0x" << std::uppercase << std::hex <<
			std::setw(2) << std::setfill('0') <<
			(unsigned) (unsigned char) it->first << ": [b\"";
		if (it->second->encoded)
			os << it->second->encoded;
		os << "\", ";
		if (it->second->children.empty())
			os << "None";
		else
			PrintTreeNode(os, &it->second->children, indent + 1);
		if (++it != tree_node->end())
			os << "],\n";
		else
		{
			os << "]\n";
			break;
		}
	}
	PrintIndent(indent, os);
	os << '}';
}

int main(int argc, const char* argv[])
{
	if (argc != 2)
	{
		std::cerr << "Usage: " << *argv << " OUTPUT_FILE" << std::endl;
		return 1;
	}

	const std::string output_file_name = argv[1];

	std::stringstream ss;

	if (!(ss << std::ifstream(output_file_name).rdbuf()))
	{
		std::cerr << output_file_name << ": IO error" << std::endl;
		return 1;
	}

	std::string python_code = ss.str();

	const size_t xlat_tree_pos = python_code.find(XLAT_TREE_BEGIN);

	if (xlat_tree_pos == std::string::npos)
	{
		std::cerr << output_file_name <<
			": couldn't locate generated content" << std::endl;
		return 1;
	}

	size_t xlat_tree_end_pos =
		python_code.find(XLAT_TREE_END, xlat_tree_pos);

	if (xlat_tree_end_pos == std::string::npos)
	{
		std::cerr << output_file_name << ": no closing bracket "
			"for generated content" << std::endl;
		return 1;
	}

	xlat_tree_end_pos += sizeof(XLAT_TREE_END) - 1;

	XLatTreeGenerator generator;

	// For each input UTF-8 character.
	for (int i = 0; i < NUMBER_OF_ENTRIES; ++i)
		generator.AddXLatEntry(xlat_entries + i);

	// Replace generated content.
	python_code.replace(xlat_tree_pos, xlat_tree_end_pos - xlat_tree_pos,
		generator.GenerateXLatTree());

	std::ofstream os(output_file_name);
	os.write(python_code.data(), python_code.length());

	return 0;
}
