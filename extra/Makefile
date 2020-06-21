.PHONY: clean

../src/anglicize.py: make_xlat_tree
	./make_xlat_tree $@

make_xlat_tree: make_xlat_tree.cpp xlat_entries.h
	$(CXX) -o $@ $<

clean:
	rm -f make_xlat_tree
