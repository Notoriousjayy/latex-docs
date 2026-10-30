.PHONY: validate test-cpp test-python pdf-sample clean
validate:
	python3 scripts/validate_suite.py

test-python:
	python3 -m unittest discover -s code/python/tests -v

test-cpp:
	cmake -S code/cpp -B /tmp/gea-cpp-build -DCMAKE_BUILD_TYPE=Debug
	cmake --build /tmp/gea-cpp-build -j 4
	ctest --test-dir /tmp/gea-cpp-build --output-on-failure

pdf-sample:
	cd curriculum && latexmk -pdf -interaction=nonstopmode -halt-on-error prerequisite-based-curriculum.tex

clean:
	find . -type f \( -name '*.aux' -o -name '*.fdb_latexmk' -o -name '*.fls' -o -name '*.log' -o -name '*.out' -o -name '*.pdf' \) -delete
