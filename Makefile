.PHONY: all clean

all: make_xlat_tree

make_xlat_tree: make_xlat_tree.cpp xlat_entries.h
	$(CXX) -o make_xlat_tree make_xlat_tree.cpp
