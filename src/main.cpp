#include <iostream>
#include <fstream>
#include <vector>
#include <nlohmann/json.hpp>

using json = nlohmann::json;
using namespace std;

vector<string> loadChampionData() {
    ifstream file("data\\champions.json");
    vector<string> champions;

    if (!file) {
        cerr << "Error: Unable to open champions.json. Run riot_api.py first." << endl;
        return champions;
    }

    json data;
    file >> data;

    for (const auto& champ : data) {
        champions.push_back(champ);
    }

    return champions;
}

int main() {
    vector<string> champions = loadChampionData();

    cout << "Loaded Champions:" << endl;
    for (const auto& champ : champions) {
        cout << champ << endl;
    }

    return 0;
}
