#
# Makefile
#
# Identical pion makefile
#

ALIROOT = aliroot


.PHONY: all run run_grid clean


all: ConfigFemtoAnalysis.C


run: ConfigFemtoAnalysis.C
	aliroot -q -x RunMe.C

run_grid:
	aliroot -q -x RunOnGrid.C

%.C: src/%.C
	cp $< $@

clean:
	rm -rf *.o AutoDict*
