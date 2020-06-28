// This program updates the XLAT_TREE structure inside anglicize.py.

#include <map>
#include <string>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <cassert>

#include <map>

// UTF-8 char to roman representation correspondence.
struct XLatEntry
{
	const char* from;
	const char* to;
};

// Load input data.
#include "xlat_entries.h"

#define XLAT_TREE_BEGIN "\n    XLAT_TREE: Dict[int, Any] = "
#define XLAT_TREE_END "\n    }"

struct XLatTreeNode;

// NodeMap matches the XLAT_TREE structure in ../src/anglicize.py.
typedef std::map<char, std::unique_ptr<XLatTreeNode>> NodeMap;

struct XLatTreeNode
{
	const char* encoded;
	NodeMap children;

	XLatTreeNode(const char* encoded) : encoded(encoded)
	{
	}
};

// Build a tree out of byte sequences of the input UTF-8 characters.
static void add_xlat_entry(NodeMap& xlat_tree_root, const XLatEntry& xlat_entry)
{
	const char* ch = xlat_entry.from;

	assert(*ch != '\0');

	// Create nodes in the output tree for all but the last
	// byte in the input UTF-8 character.

	auto [node, inserted] = xlat_tree_root.emplace(*ch, nullptr);

	while (*++ch != '\0')
	{
		if (inserted)
			node->second = std::make_unique<XLatTreeNode>(nullptr);

		std::tie(node, inserted) =
			node->second->children.emplace(*ch, nullptr);
	}

	// Mark the node of the last byte as final by assigning
	// the transliteration of the UTF-character to it.
	if (inserted)
		node->second = std::make_unique<XLatTreeNode>(xlat_entry.to);
	else
	{
		assert(node->second->encoded == nullptr &&
			"Duplicate entries are not allowed");

		node->second->encoded = xlat_entry.to;
	}
}

static void print_indent(int indent, std::ostream& os)
{
	while (--indent >= 0)
		os << "    ";
}

static void print_tree_node(
	std::ostream& os, const NodeMap& tree_node, int indent)
{
	os << "{\n";
	NodeMap::const_iterator it = tree_node.begin();
	for (;;)
	{
		print_indent(indent + 1, os);
		os << "0x" << std::uppercase << std::hex <<
			std::setw(2) << std::setfill('0') <<
			(unsigned) (unsigned char) it->first << ": [b\"";
		if (it->second->encoded)
			os << it->second->encoded;
		os << "\", ";
		if (it->second->children.empty())
			os << "None";
		else
			print_tree_node(os, it->second->children, indent + 1);
		if (++it != tree_node.end())
			os << "],\n";
		else
		{
			os << "]\n";
			break;
		}
	}
	print_indent(indent, os);
	os << '}';
}

int main(int argc, const char* argv[])
{
	if (argc != 2)
	{
		std::cerr << "Usage: " << *argv <<
			" ../src/anglicize.py" << std::endl;
		return 1;
	}

	const std::string py_pathname = argv[1];

	std::string py_code;

	// Read anglicize.py contents into 'py_code'.
	if (std::stringstream ss;
			(ss << std::ifstream(py_pathname).rdbuf()))
		py_code = ss.str();
	else
	{
		std::cerr << py_pathname << ": IO error" << std::endl;
		return 1;
	}

	size_t xlat_tree_pos = py_code.find(XLAT_TREE_BEGIN);

	if (xlat_tree_pos == std::string::npos)
	{
		std::cerr << py_pathname <<
			": couldn't locate generated content" << std::endl;
		return 1;
	}

	xlat_tree_pos += sizeof(XLAT_TREE_BEGIN) - 1;

	size_t xlat_tree_end_pos =
		py_code.find(XLAT_TREE_END, xlat_tree_pos);

	if (xlat_tree_end_pos == std::string::npos)
	{
		std::cerr << py_pathname << ": no closing bracket "
			"for generated content" << std::endl;
		return 1;
	}

	xlat_tree_end_pos += sizeof(XLAT_TREE_END) - 1;

	NodeMap xlat_tree_root;

	// For each input UTF-8 character.
	for (const auto xlat_entry : xlat_entries)
		add_xlat_entry(xlat_tree_root, xlat_entry);

	// Rewrite anglicize.py.
	std::ofstream os(py_pathname);

	os.write(py_code.data(), xlat_tree_pos);

	print_tree_node(os, xlat_tree_root, 1);

	os.write(py_code.data() + xlat_tree_end_pos,
		py_code.length() - xlat_tree_end_pos);

	return 0;
}
