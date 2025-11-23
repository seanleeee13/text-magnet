#include <iostream>
#include <algorithm>
#include <string>
#include <vector>
#include <set>
#include "words.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

using namespace std;

namespace py = pybind11;

int diff;

set<string> calculate(string a) {
    set<string> word_n;
    vector<string> sp_n;
    if (a.length() < 5) {
        diff = 0;
        return word_n;
    }
    set<string> s;
    sort(a.begin(), a.end());
    do {
        s.insert(a);
    } while (next_permutation(a.begin(), a.end()));
    set_intersection(words.begin(), words.end(), s.begin(), s.end(), inserter(word_n, word_n.begin()));
    diff = 5 * word_n.size();
    set_intersection(word_n.begin(), word_n.end(), special.begin(), special.end(), sp_n.begin());
    if (sp_n.size() > 0) {
        if (word_n.find(most_special) != word_n.end()) {
            diff += 45;
        } else {
            diff += 15;
        }
    }
    return word_n;
}

int get_diff() {
    return diff;
}

PYBIND11_MODULE(process, m) {
    m.def("calculate", &calculate, "word calculation");
    m.def("get_diff", &get_diff, "getting score difference");
}