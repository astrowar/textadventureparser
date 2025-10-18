#include <string.h>


typedef struct {
    const char *word;
    int code;
} DictEntry;

static DictEntry corpus[] = {
    // Verbos de ação
    {"pega", 100},
    {"abre", 101},
    {"olha", 102},
    {"examina", 103},
    {"entra", 104},
    {"sai", 105},
    {"vai", 106},
    {"anda", 107},
    {"fala", 108},
    {"usa", 109},
    {"empurra", 110},
    {"puxa", 111},
    {"sobe", 112},
    {"desce", 113},
    {"ataca", 114},
    {"espera", 115},
    {"dá", 116},
    {"deixa", 117},

    // Artigos definidos
    {"o", 200},
    {"a", 201},
    {"os", 202},
    {"as", 203},

    // Artigos indefinidos
    {"um", 204},
    {"uma", 205},
    {"uns", 206},
    {"umas", 207},

    // Preposições
    {"em", 300},
    {"no", 301},
    {"na", 302},
    {"nos", 303},
    {"nas", 304},
    {"de", 305},
    {"do", 306},
    {"da", 307},
    {"dos", 308},
    {"das", 309},
    {"com", 310},
    {"para", 311},
    {"por", 312},
    {"sobre", 313},
    {"até", 314},
    {"após", 315},
    {"entre", 316},
    {"contra", 317},
};

static DictEntry corpus_extra[] = {
    // Substantivos comuns (objetos, locais, coisas)
    {"chave", 400},
    {"porta", 401},
    {"janela", 402},
    {"mesa", 403},
    {"cadeira", 404},
    {"livro", 405},
    {"tocha", 406},
    {"espada", 407},
    {"escudo", 408},
    {"cofre", 409},
    {"baú", 410},
    {"chão", 411},
    {"parede", 412},
    {"sala", 413},
    {"cozinha", 414},
    {"jardim", 415},
    {"corredor", 416},
    {"guarda", 417},
    {"monstro", 418},
    {"tesouro", 419},
    {"caverna", 420},
    {"porta secreta", 421},

    // Adjetivos comuns
    {"velha", 500},
    {"velho", 501},
    {"nova", 502},
    {"novo", 503},
    {"grande", 504},
    {"pequeno", 505},
    {"pesada", 506},
    {"pesado", 507},
    {"leve", 508},
    {"escura", 509},
    {"escuro", 510},
    {"vermelha", 511},
    {"vermelho", 512},
    {"azul", 513},
    {"verde", 514},
    {"quebrada", 515},
    {"quebrado", 516},
    {"misteriosa", 517},
    {"misterioso", 518},
};

static DictEntry corpus_template[] = {
    {"X", 999},
};

static const int corpus_size = sizeof(corpus) / sizeof(corpus[0]);
static const int corpus_extra_size = sizeof(corpus_extra) / sizeof(corpus_extra[0]);
static const int corpus_template_size = sizeof(corpus_template) / sizeof(corpus_template[0]);

// implementação de getDict
int getDict(char *p, int len) {
    for (int i = 0; i < corpus_size; i++) {
        if ((int)strlen(corpus[i].word) == len &&
            strncmp(p, corpus[i].word, len) == 0) {
            return corpus[i].code;
        }
    }
    //try extra corpus, adjetivo + noum OR noum
    for (int i = 0; i < corpus_extra_size; i++) {
        if ((int)strlen(corpus_extra[i].word) == len &&
            strncmp(p, corpus_extra[i].word, len) == 0) {
            return corpus_extra[i].code;
        }
    }
    //templates special words
    for (int i = 0; i < corpus_template_size; i++) {
        if ((int)strlen(corpus_template[i].word) == len &&
            strncmp(p, corpus_template[i].word, len) == 0) {
            return corpus_template[i].code;
        }
    }

    return 0; // não encontrado
}