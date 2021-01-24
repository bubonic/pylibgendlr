#!/bin/bash
#
# Extract IDs  of books from http://gen.lib.rus.ec

if [ "$#" -ne 1 ]; then
    echo "Usage: "
    echo "$0 searchterm "
    echo "Besure to use a '+' where spaces go in searchterm"
    echo "Example: $0 Automorphic+Forms"
    exit 0
fi
#curl "http://gen.lib.rus.ec/search.php?&req=Automorphic+forms&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page=1" | grep "md5=" | cut -d = -f 3 | cut -d \' -f 1
#curl "http://gen.lib.rus.ec/search.php?&req=Automorphic+forms&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page=1" | grep "md5=" | cut -d = -f 3 | cut -d \' -f 1 | sed '/^$/d' | uniq


#Get Number of books
NUM_OF_BOOKS=`curl -v -A "Mozilla/5.0 (X11; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0" -e "http://gen.lib.rus.ec/"  "http://gen.lib.rus.ec/search.php?&req="$1"&open=0&view=simple&phrase=1&column=def" | grep "files found" | sed 's/files found.*//' | sed 's/.*>//'`

# print characters after last instance of >
#grep "books found" | sed 's/books found.*//' | sed 's/.*>//'

echo "Number of books in search is: $NUM_OF_BOOKS"
sleep 20

# Do so math to figure out the number of pages
if [ "$NUM_OF_BOOKS" -gt "25" ]; then
	R=$(($NUM_OF_BOOKS % 25))
	#echo "Remainder: $R"
	MULTIPLE=$((($NUM_OF_BOOKS - $R)/25))
	if [ "$R" -gt "0" ]; then
		PAGES=$(($MULTIPLE+1))
	else
		PAGES=$MULTIPLE
	fi
else
	PAGES=1
fi
echo "The number of pages to scrape is: $PAGES" 
echo "Getting MD5sums of books in $PAGES pages of search results"
#Get MD5 sums of the books
PAGE_I=1
DIR_NAME="${1//+/_}"

if [ ! -d "$DIR_NAME" ]; then
	mkdir $DIR_NAME
else
	echo "$DIR_NAME exists"
fi


cd $DIR_NAME
PAGE_I_1=1
echo "Changing Directory to $DIR_NAME"
while [ $PAGE_I -le $PAGES ]; do
	echo "Getting IDs on page: $PAGE_I"
	if [ "$PAGE_I" -eq 1 ]; then
		echo "Using domain name as referer"
#		curl -v -A "Mozilla/5.0 (X11; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0" -e "http://gen.lib.rus.ec/" "http://gen.lib.rus.ec/search.php?&req="$1"&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page="$PAGE_I | grep "md5=" | cut -d = -f 3 | cut -d \' -f 1 | sed '/^$/d' | uniq >> $1.md5sums
#		curl -v -A "Mozilla/5.0 (X11; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0" -e "http://gen.lib.rus.ec/" "http://gen.lib.rus.ec/search.php?&req="$1"&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page="$PAGE_I | grep "md5=[a-Z,0-9]" | cut -d "'" -f 2 | grep "libgen.io" | cut -d "=" -f 2 >> $1.md5sums
		curl -v -A "Mozilla/5.0 (X11; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0" -e "http://gen.lib.rus.ec/" "http://gen.lib.rus.ec/search.php?&req="$1"&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page="$PAGE_I | grep "libgen.pw" | cut -d "]" -f 4 | grep -o "href='[^']*" | sed "s/href='//g" | sed 's/.*id\///g' >> $1.IDs
	else
		echo "Using referer page $PAGE_I_1"
#		curl -v -A "Mozilla/5.0 (X11; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0" -e "http://gen.lib.rus.ec/search.php?&req="$1"&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page="$PAGE_I_1 "http://gen.lib.rus.ec/search.php?&req="$1"&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page="$PAGE_I | grep "md5=" | cut -d = -f 3 | cut -d \' -f 1 | sed '/^$/d' | uniq >> $1.md5sums
#		curl -v -A "Mozilla/5.0 (X11; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0" -e "http://gen.lib.rus.ec/search.php?&req="$1"&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page="$PAGE_I_1 "http://gen.lib.rus.ec/search.php?&req="$1"&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page="$PAGE_I | grep "md5=[a-Z,0-9]" | cut -d "'" -f 2 | grep "libgen.io" | cut -d "=" -f 2  >> $1.md5sums
		curl -v -A "Mozilla/5.0 (X11; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0" -e "http://gen.lib.rus.ec/search.php?&req="$1"&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page="$PAGE_I_1 "http://gen.lib.rus.ec/search.php?&req="$1"&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page="$PAGE_I | grep "libgen.pw" | cut -d "]" -f 4 | grep -o "href='[^']*" | sed "s/href='//g" | sed 's/.*id\///g'  >> $1.IDs
	fi
	let PAGE_I=PAGE_I+1
	PAGE_I_1=$((PAGE_I - 1))
	sleep 20
done
#count=0
#
#while read md5sum; do 
#	let count++
#	m=`expr $count % 4`
#	while [ $m -eq 0 ]; do
#		echo -ne "Changing Proxies..."
#		proxy=`shuf -n 1 /home/bubonic/Proxies/hanon`
#		proxy_addr=`echo $proxy | awk -F: '{print $1}'`
#		proxy_port=`echo $proxy | awk -F: '{print $2}'`
#		HPROXY=`echo "http://$proxy_addr:$proxy_port/"`
#		nc -w 5 -z $proxy_addr $proxy_port
#		if [ $? -eq "0" ]; then
#			echo -ne "Connection to $HPROXY is a success!\n"
#       	        http_proxy=$HPROXY
#	                `export http_proxy`
#       	        break
#           	else
#                	echo "Connection to $HPROXY  failed!"
#           	fi
#	done
#	TITLE=`curl -s -A "User-Agent: Mozilla/5.0 (Windows NT 5.1; rv:23.0) Gecko/20100101 Firefox/23.0" -e "http://gen.lib.rus.ec/search.php?&req="$1"&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page=1" "http://bookfi.org/md5/"$md5sum | grep "itemprop=\"name\"" | cut -d ">" -f 3 | cut -d "<" -f 1`
#	AUTHOR=`curl -s -A "User-Agent: Mozilla/5.0 (Windows NT 5.1; rv:23.0) Gecko/20100101 Firefox/23.0" -e "http://gen.lib.rus.ec/search.php?&req="$1"&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page=1"  "http://bookfi.org/md5/"$md5sum | grep "itemprop=\"author\"" | cut -d ">" -f 2 | cut -d "<" -f 1`
#       echo "$TITLE by $AUTHOR"
#	LINK=`curl -s -A "User-Agent: Mozilla/5.0 (Windows NT 5.1; rv:23.0) Gecko/20100101 Firefox/23.0" -e "http://gen.lib.rus.ec/search.php?&req="$1"&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page=1" "http://bookfi.org/md5/"$md5sum | grep "Электронная библиотека скачать книгу" | grep "href=" | cut -d "=" -f 5 | cut -d '"' -f 2`
#	echo "Link to book: $LINK"
#	FILE_TYPE=`curl -s -A "User-Agent: Mozilla/5.0 (Windows NT 5.1; rv:23.0) Gecko/20100101 Firefox/23.0" -e "http://gen.lib.rus.ec/search.php?&req="$1"&phrase=1&view=simple&column=def&sort=title&sortmode=ASC&page=1" "http://bookfi.org/md5/"$md5sum | grep "Электронная библиотека скачать книгу" | grep "href=" | cut -d ">" -f 3 | cut -d "(" -f 2 | cut -d ")" -f 1`
#       FILE_TYPE_LC=${FILE_TYPE,,}
#       echo "File type: $FILE_TYPE_LC"
#	FILE_NAME="$TITLE by $AUTHOR"+"."+$FILE_TYPE_LC
#	echo "File name: $FILE_NAME"
#	sleep 20
#	wget -O $FILE_NAME --user-agent="User-Agent: Mozilla/5.0 (Windows NT 5.1; rv:23.0) Gecko/20100101 Firefox/23.0" --referer $LINK $LINK
#
# wget to http://scienceengineering.library.scilibgen.org
#       wget -O Bellison_L-function.djvu --user-agent="User-Agent: Mozilla/5.0 (Windows NT 5.1; rv:23.0) Gecko/20100101 Firefox/23.0" --referer "http://scienceengineering.library.scilibgen.org/view.php?id=4101" "http://store-k.free-college.org/noleech1.php?hidden=%2F4000%2F71f81875dd8f2d5990771b40f64577d8&hidden0=M.+Rapoport%2C+N.+Schappacher%2C+P.+Schneider+Beilinson%27s+conjectures+on+special+values+of+L-functions.djvu&submit=+GET\!\+"
#done < $1.md5sums
#libgen download link?
#http://libgen.education/get.php?md5=5c58f0afab8041167a9d0b3e7c7d54bf
