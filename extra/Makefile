.PHONY: clean

../src/anglicize.py: make_xlat_tree
	./make_xlat_tree $@

make_xlat_tree: make_xlat_tree.cpp xlat_entries.h
	$(CXX) -std=c++17 -o $@ $<

clean:
	rm -f make_xlat_tree
