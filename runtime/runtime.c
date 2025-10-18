#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdlib.h>






//============================


#define MAX_TOKENS 128
#define MAX_WORD   64

// Resultado de cada token
typedef struct {
    char word[MAX_WORD]; // a palavra ou frase reconhecida
    int code;            // código do dicionário, ou -1 se não encontrado
} TokenResult;

// Resultado geral do parser
typedef struct {
    TokenResult tokens[MAX_TOKENS];
    int count;      // quantos tokens foram preenchidos
    int hasError;   // 1 se alguma palavra não foi encontrada
} ParseResult;

typedef struct  Action{
    int verb; // verbo
    int noun; // substantivo
    int noum2; // adjetivo opcional

    //local
    int location; // local onde a ação ocorre
    int actor;
} Action;


//convert an list of dict words intro an action
typedef struct ActionTemplate{
    int verb; // verbo
    int noun; // substantivo
    int noum2;
    int noum3;
}ActionTemplate;


//Values can be text, number, object reference
typedef struct TextValue{
    char *text[255];
}TextValue;

typedef struct NumberValue{
    int value;
}NumberValue;

typedef struct ObjectValue{
    int objectId;
}ObjectValue;

//  entity is any object in the world derivade from Thing
// piano - musical instrument
// location: in the Studio
// singular-named, improper-named; unlit, inedible, portable
// list grouping key: none
// printed name: "piano"
// printed plural name: "musical instruments"
// indefinite article: none
// description: none
// initial appearance: none


typedef struct Entity{
    int id;
    char name[32];
    int location; // current location

    //propriedade no runtime ja vem processada
    char *printedName;
    char *printedPluralName;
    char *indefiniteArticle;
    char *description;
    char *initialAppearance;

}Entity;

typedef struct Kind{
} Kind;

//A thing is a kind.
// A thing can be lit or unlit.
// A thing is usually unlit.
// A thing can be edible or inedible.
// A thing is usually inedible.
// A thing can be fixed in place or portable.
// A thing is usually portable.
// A thing can be scenery.
// A thing can be wearable.
// A thing can be pushable between rooms.
// A thing can be handled.
// A thing can be privately-named or publicly-named.
// A thing is usually publicly-named.
// A thing can be described or undescribed.
// A thing is usually described.
// A thing can be marked for listing or unmarked for listing.
// A thing is usually unmarked for listing.
// A thing can be mentioned or unmentioned.
// A thing is usually mentioned.
// A thing has a text called a description.
// A thing has a text called an initial appearance.

typedef struct Thing {
    Entity baseEntity;
    int _lit_unlit; // 1 = lit, 0 = unlit
    int _edible_inedible; // 1 = edible, 0 = inedible
    int _fixed_portable; // 1 = fixed in place, 0 = portable
    int _scenery; // 1 = scenery, 0 = not scenery
    int _wearable; // 1 = wearable, 0 = not wearable
    int _pushable; // 1 = pushable between rooms, 0 = not pushable
    int _handled; // 1 = handled, 0 = not handled
    int _privately_publicly_named; // 1 = privately-named, 0 = publicly-named
    int _described_undescribed; // 1 = described, 0 = undescribed
    int _listed_unlisted; // 1 = marked for listing, 0 = unmarked for listing
    int _mentioned_unmentioned; // 1 = mentioned, 0 = unmentioned
    char *description;
    char *initialAppearance;
} Thing;


//A person has a number called carrying capacity. The carrying capacity of a person is usually 100.


//A person is a kind of thing.
typedef struct Person{
    Thing baseThing;
      //A person can be female or male. A person is usually male.
    int _male_female; // 1 = male, 0 = female
    // A person can be neuter. A person is usually not neuter.
    int _neuter; // 1 = neuter, 0 = not neuter
    int _carrying_capacity; // default 100
} Person;

void init_Person( Person *p){
    p->baseThing = (Thing){};
    p->_male_female = 1; // A person is usually male.
    p->_neuter = 0; // A person is usually not neuter
    p->_carrying_capacity = 100; // default 100
}


typedef struct World {
    int gameOver;
    ActionTemplate actionTemplates[10];

    //global variables
     //The player is a person that varies.
    Person player;
    //The yourself is an undescribed person. The yourself is proper-named.
    Person yourself;

}World;



//check if C start with an compose woird in dict, return the id code, and the next word tyhats not belonging to the compose word
// the red carpet and the book
// [the red carpet] -> id = 34, nextWordPtr points to  "and the book"
 int getDict(char *p, int len);

// Função auxiliar para pular espaços
// pula espaços

static char *skipSpaces(char *p) {
    while (*p && isspace((unsigned char)*p)) p++;
    return p;
}
 // Função de parsing (retorna 0 se sucesso, -1 se houve erro)
int parseText(char *text, ParseResult *result) {
    result->count = 0;
    result->hasError = 0;

    char *p = skipSpaces(text);
    while (*p && result->count < MAX_TOKENS) {
        char *best_end = NULL;
        int best_code = 0;
        int best_len = 0;

        char *q = p;
        while (*q) {
            q++;
            if (*q != '\0' && !isspace((unsigned char)*q)) {
                continue;
            }

            int span_len = q - p;
            int code = getDict(p, span_len);

            if (code > 0) {
                best_code = code;
                best_end = q;
                best_len = span_len;
            }

            if (*q == '\0') break;
        }

        TokenResult *tok = &result->tokens[result->count++];

        if (best_code > 0) {
            strncpy(tok->word, p, best_len);
            tok->word[best_len] = '\0';
            tok->code = best_code;
            p = skipSpaces(best_end);
        } else {
            // palavra não encontrada
            char *q2 = p;
            while (*q2 && !isspace((unsigned char)*q2)) q2++;
            int span_len = q2 - p;

            strncpy(tok->word, p, span_len);
            tok->word[span_len] = '\0';
            tok->code = -1;
            result->hasError = 1;

            p = skipSpaces(q2);
        }
    }

    return result->hasError ? -1 : 0;
}








void registerActionTemplate( ParseResult r, ActionTemplate *t){
    //assume the first token is the verb
    if( r.count < 1) return;
    t->verb = r.tokens[0].code;
    t->noun = (r.count > 1) ? r.tokens[1].code : 0;
    t->noum2 = (r.count > 2) ? r.tokens[2].code : 0;
    t->noum3 = (r.count > 3) ? r.tokens[3].code : 0;

    printf("Registered action template: verb=%d, noun=%d, noum2=%d, noum3=%d\n",
           t->verb, t->noun, t->noum2, t->noum3);

}

void registerActions(ActionTemplate *templates ){
    //store in a global array
    // olha

    ParseResult r;
    int status = parseText("olha", &r);
    registerActionTemplate( r, templates);  templates++;
    status = parseText("olha para X", &r);
    registerActionTemplate( r, templates);  templates++;
    status = parseText("pega X", &r);
    registerActionTemplate( r, templates);  templates++;
}

void init( World *w){
    w->gameOver = 0;
    registerActions(  w->actionTemplates );

}


void update(World *w, ParseResult *r){

    Action a;
    a.verb = (r->count > 0) ? r->tokens[0].code : 0;
    a.noun = (r->count > 1) ? r->tokens[1].code : 0;
    a.noum2 = (r->count > 2) ? r->tokens[2].code : 0;
    a.location = w->player.location;
    a.actor = w->player.id;



}


int game_loop(World *w){
    //read input
    char input[50];


    while( !w->gameOver ){
        printf(">> ");
        fgets(input, sizeof(input), stdin);
        //stdin receive an ctrl-D ?
        if( feof(stdin) ) break;
        input[strcspn(input, "\n")] = 0; // remove newline


        ParseResult r;
        int status = parseText(input, &r);
        for (int i = 0; i < r.count; i++) {
            printf("[%s:%d] ", r.tokens[i].word, r.tokens[i].code);
        }
        printf("\n");

        //update world state
        update(w, &r);
    }

    printf("Game Over!\n");
    return 0;


}


int main(){
    //runtime from text adventure.
    World w;
    init(&w);
    game_loop(&w);

    return 0;

}