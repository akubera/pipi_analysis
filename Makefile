#
# Makefile
#
# Identical pion makefile
#

ALIROOT = aliroot


.PHONY: all run run_grid clean


all:


run: RunMe.C
	aliroot -q -x $<

run_grid: RunGrid.C
	aliroot -q -x $<

%.C: src/%.C
	cp $< $@


clean:
	rm -rf *.o AutoDict*
