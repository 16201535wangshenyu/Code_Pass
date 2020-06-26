<template>
        <div class="page">
            <div >
                <label for="title">Title</label>
                <input type="text"  class="title" name="title" id="title" v-model="title" placeholder="Enter a title" />

                <label for="container">Content</label>
                <div id="container" v-text="content"> </div>
              <!--  <textarea class="content" name="content" v-model="page.content" placeholder="Enter some content"></textarea> -->
                <button @click="deletePage()">Delete Page</button>
                <button @click="savePage()">Save Page</button>
            </div>
          <!--  <div v-else>
                <h1>&larr; To start, create a new page!</h1>
            </div> -->
        </div>
    </template>
    <script>
    import * as monaco from "monaco-editor";

      export default {
        name: 'JavaEditor',
        // props: ['page'],
        data(){
            return {
                title : "Main.java",
                content : "public class Main_01 {\n" +
                    "    private int i = 0;\n" +
                    "    public static void main(String[] args) {\n" +
                    "        for(int i =1;i<100;i++){ \n" +
                    "            if(isPrime(i))\n" +
                    "            {\n" +
                    "                System.out.println(i);\n" +
                    "            }\n" +
                    "        }\n" +
                    "    }\n" +
                    "    public static boolean isPrime(int num){\n" +
                    "        if(num == 1)\n" +
                    "            return false;  \n" +
                    "        long sprtNum = (long)Math.sqrt(num);\n" +
                    "        for(int i=2;i<=sprtNum;i++){\n" +
                    "            if(num%i==0){         \n" +
                    "                return false;    \n" +
                    "            }\n" +
                    "        }\n" +
                    "        return true;\n" +
                    "    }\n" +
                    "}",
            }

        },
        methods: {
          deletePage () {
            this.$emit('delete-page')
          },
          savePage () {
            this.$emit('save-page')
          }
        }, 
        mounted(){
            monaco.languages.registerCompletionItemProvider("java", {
              // eslint-disable-next-line no-unused-vars
              provideCompletionItems: (model, position) => {
                return [
                  {
                    label: "apiVersion",
                    kind: monaco.languages.CompletionItemKind.Function,
                    documentation: "Defines the version of Api to create the object",
                    detail: "Required Field"
                  }
                ];
              }
            });

            monaco.languages.registerSignatureHelpProvider("java", {
              signatureHelpTriggerCharacters: ["(", ","],
              // eslint-disable-next-line no-unused-vars
              provideSignatureHelp: (model, position, token) => {
                return {
                  activeParameter: 0,
                  activeSignature: 0,
                  signatures: [
                    {
                      label:
                        "string substr(string $string, int $start [, int $length])",
                      parameters: [
                        {
                          label: "string $string",
                          documentation:
                            "The input string. Must be one character or longer."
                        },
                        {
                          label: "int $start",
                          documentation:
                            "If $start is non-negative, the returned string will start at the $start'th position in string, counting from zero. For instance, in the string 'abcdef', the character at position 0 is 'a', the character at position 2 is 'c', and so forth.\r\nIf $start is negative, the returned string will start at the $start'th character from the end of string. If $string is less than $start characters long, FALSE will be returned."
                        },
                        {
                          label: "int $length",
                          documentation:
                            "If $length is given and is positive, the string returned will contain at most $length characters beginning from $start (depending on the length of $string) If $length is given and is negative, then that many characters will be omitted from the end of $string (after the start position has been calculated when a start is negative). If $start denotes the position of this truncation or beyond, FALSE will be returned. If $length is given and is 0, FALSE or NULL, an empty string will be returned. If $length is omitted, the substring starting from $start until the end of the string will be returned."
                        }
                      ]
                    }
                  ]
                };
              }
            });

            monaco.editor.create(document.getElementById("container"), {
              value: "",
              language: "java",
              theme: "vs-dark",
              fontSize: "25px"
            });
        }
      }
    </script>

    <style scoped>
        .page {
            width: 100%;
            padding: 2rem;
            box-shadow: 3rem 0 5rem 3rem #c1f5ff;
        }

        .content, .title {
            border-style: none;
            border-radius: 0.25rem;
            border: solid 1px lightgray;
            width: 100%;
            box-sizing: border-box;
            margin-bottom: 1.25rem;
        }

        .content:focus, .title:focus {
            outline: 0;
        }

        .content {
            font-family: 'Avenir', Helvetica, Arial, sans-serif;
            resize: vertical;
            font-size: 1.5rem;
            padding: 0.5rem;
            height: 20rem;
        }

        .title {
            font-size: 2rem;
            padding: 0.5rem 1rem;
        }

        label {
            margin-bottom: 0.5rem;
            display: inline-block;
        }

        button {
            border-style: none;
            padding: 0.5rem 0.75rem;
            background-color: #44abc3;
            margin-right: 2rem;
            border-radius: 0.25rem;
            color: white;
            font-size: 1rem;
            cursor: pointer;
        }

        button:hover {
            background-color: #368ea2;
        }

        #container {
            height: 30rem;
            width: 50rem;
        }

    </style>