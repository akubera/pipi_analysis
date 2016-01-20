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

multi_run:
	for i in {1..8}; do aliroot -q -x src/RunMe.C $$i & sleep 4; done

multi_run_11:
	for i in {1..8}; do aliroot -q -x src/RunParallel_11.C $$i TEMP_RESULT.root & sleep 4; done

run_grid: RunGrid.C
	aliroot -q -x $<

%.C: src/%.C
	cp $< $@


clean:
	rm -rf *.o AutoDict*
