#!/bin/bash

usage() {
  echo "Usage: $0 [ -f FILE ] [ -o OUTPUT ] [ -t TYPE ]" 1>&2
  echo ""
  echo "   -f Input ipynb file (default: )"
  echo "   -o Output filename (default: same as input)"
  echo "   -t Output type pdf or html (default: pdf)"
  echo "   -c flag for including input code in output"
}

exit_abnormal() {
  usage
  exit 1
}

excludeCode="True"

while getopts ":f:o:t:c" opt; do
  case "${opt}" in
    f) FILE=${OPTARG};;
    o) OUTPUT=${OPTARG};;
    t) TYPE+=("${OPTARG}");;
    c) excludeCode="False";;
    :)
      echo "Error: -${OPTARG} requires an argument."
      exit_abnormal
      ;;
    *)
      exit_abnormal
      ;;
  esac
done

if [ "$FILE" == "" ]; then
    exit_abnormal
else
    input=$FILE
fi

if [ "$OUTPUT" == "" ]; then
    output=`echo $input | cut -d'.' -f1`
else
    output=$OUTPUT
fi
echo $output

if [ "$TYPE" == "" ]; then
    TYPE=("pdf")
fi

for type in ${TYPE[*]}; do
    if [ "$type" == "pdf" ]; then
      python -m jupyter nbconvert --to pdf ${input} --output ${output}.pdf  --PDFExporter.exclude_input=${excludeCode}
    fi

    if [ "$type" == "html" ]; then
        python -m jupyter nbconvert --to html ${input} --output ${output}.html  --TemplateExporter.exclude_input=${excludeCode}
    fi
done
exit
