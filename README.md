<h1><a id="Sentry Breakpad Server"></a>Sentry Breakpad Server</h1>


<p>Hello, this a set of scripts used to act as an intermediate processor between a minidump file uploaded to a bucket, to Sentry, an open-source Web UI for storing and displaying error reports. It’s intended purpose is to be used to allow for a unified source to access, sort, and query crash reports/stack traces across multiple devices and builds. So when a device integrated with Google Breakpad crashes, it will create a minidump file and send it to an Amazon Bucket via Antenna, a web collector app developed by Mozilla. Antenna has been modified to then call this set of scripts which downloads the file, processes it into a stack trace with Breakpad (explained below), and then parses the stack trace and sends it to Sentry.</p>
<h2><a id="What_youll_need_6"></a>What you’ll need:</h2>
<ul>
<li>
<p><strong>Antenna</strong> (<a href="https://github.com/mozilla-services/antenna">https://github.com/mozilla-services/antenna</a>)</p>
</li>
<li>
<p>An <strong>Amazon Bucket</strong> for Antenna to send files to (the default instance of Antenna sends it to a localstack, but we have the bucket set to breakpad-vivint-com)</p>
</li>
<li>
<p>These <strong>Scripts</strong></p>
</li>
<li>
<p>The <strong>Google Breakpad library</strong> (<a href="https://github.com/google/breakpad">https://github.com/google/breakpad</a>) The Breakpad Library includes a library and executable to process the minidump files into stack traces</p>
<ul>
<li>NOTE: I(Matthew) stripped down and deleted a lot of the files after cloned it into the this folder as we only needed the processer part, if you wish to move this folder outside or somewhere else or want a fresh install of Breakpad, you will have to change some directories within the scripts (should only be the ‘process_dump.py’ right now)</li>
</ul>
</li>
<li>
<p>A working Instance of <strong>Sentry</strong><br>
Ours runs on a Centos Amazon Server, these were needed:<br>
- Postgresql (I implemented with 9.5)<br>
- Redis<br>
- A bunch of other dev packages that I can’t remember the name of…<br>
For help with Sentry creation…look online…here’s a general overview of what I did</p>
<ul>
<li>Get Postgresql and make database with superuser<pre><code class="language-sh">$ node app
$ psql template1
$ create user [USERNAME] with password [<span class="hljs-string">'PWD'</span>]
$ alter user [USERNAME] to superuser
$ create database [DATEBASE] with owner [USERNAME]
</code></pre>
</li>
<li>Get Redis and start it (sudo systemctl start redis.service)</li>
<li>make python virtualenv<pre><code class="language-sh">pip install -U sentry
</code></pre>
<pre><code>- sentry init
</code></pre>
(THIS CREATES 2 CONFIG FILES (default /.sentry/) where most of Sentry should be configured)
<ul>
<li>In <a href="http://sentry.conf.py">sentry.conf.py</a>, Databases should be edited to correspond with the Postgresql info created above (default host and port are 127.0.0.1 and 5432 by default)</li>
<li>Both <a href="http://sentry.conf.py">sentry.conf.py</a> and config.yml should be edited for various purposes (file storage, email, etc.)</li>
</ul>
</li>
</ul>
</li>
</ul>
<h2><a id="General_ArchitectureOverviewTODO_41"></a>General Architecture/Overview/TO-DO:</h2>
<ol>
<li>
<p>Antenna is listening (default port 8000)</p>
</li>
<li>
<p>Devices crashes and sends compressed dump file to <a href="http://brkpad.vivint.com/submit">brkpad.vivint.com/submit</a> via curl requests<br>
-<strong>TO DO [SUGGESTED]:</strong> add some authentication to this</p>
</li>
<li>
<p>Antenna calls breakpad_resource.py (in /antenna/, which calls <a href="http://crashstorage.py">crashstorage.py</a> (in /antenna/ext/s3)</p>
</li>
<li>
<p><a href="http://crashstorage.py">crashstorage.py</a> saves files to bucket<br>
-<strong>TO DO [SUGGESTED]:</strong> review file naming and path method for personalized use</p>
</li>
<li>
<p>breakpad_resource.py then calls <a href="http://boto.py">boto.py</a> in sentry_breakpad_server</p>
</li>
<li>
<p><a href="http://boto.py">boto.py</a> downloads file and calls process_dump.py</p>
</li>
<li>
<p>process_dump.py uncompresses file and uses Breakpad to process into readable stacktrace, and sends it to<br>
parse_for_sentry.py<br>
-<strong>TO DO [SUGGESTED]:</strong> Review/enable/disable how the code deletes file and/or moves them to another folder<br>
-<strong>TO DO [URGENT]:</strong> Figure how to integrate symbols, right now it just tries to look into empty folder ‘symfiles’<br>
-<strong>TO DO [URGENT]:</strong> Decide what to do with metadata, it might be in the stack trace itself, you may want to have other files in the tarfile which we will have to adjust for, have it in the filename, etc.<br>
-<strong>TO DO [IMPORTANT]:</strong> Project/DSN configuration: Right now, errors are just sent to a fixed project/DSN, but based on the various parameters of the crash, the build it came from, the model of camera, etc. you may want to create multiple projects or even teams<br>
-I suggest using the Sentry API (<a href="https://docs.sentry.io/api/">https://docs.sentry.io/api/</a>) to handle this. There are plenty of documentation in order to DELETE, RETRIEVE, or CREATE new projects/DSNs<br>
-I’ve made a script (<code>sentry_project_info.py</code>), but it is no where near finished</p>
</li>
<li>
<p>parse_for_sentry.py parses stack trace for info, message, tags, extra, stack trace<br>
-<strong>TO DO [IMPORTANT]:</strong> Review…like all of this… how you want tags to be assigned, what you want the main message to be, etc. Basically how the info is displayed on Sentry<br>
-<strong>TO DO [IMPORTANT]:</strong> Do you want to have Sentry display where in the code the crash occurred, if so, you’ll need to make the source code accessible to the server and definitely review the parse_stacktrace() method</p>
</li>
<li>
<p>The info is uploaded to Sentry (once again, the DSN is right now fixed to an test Project, please change above)</p>
</li>
</ol>
<p><strong>TO DO [SUGGESTED]:</strong> make a supervisord.service file to automatically run sentry (I already made one in<br>
/etc/supervisord.d/sentry.conf but please review)</p>
<p><strong>TO DO [IMPORTANT]:</strong> Creating Tests/Projects, viewing error and most features seem to work fine, but when I try to change the settings of a project or delete it, it goes to another URL and times out. You can carry through with the process just by adding ‘https://’ to the URL, but this is not  ideal haha. Since it involves the https:// thing I believe it has something to do with our encryption process (see nginx stuff) but I could be wrong. If problem is not a priority and/or it has yet to fix, you can delete project via terminal with API no problem</p>
<p><strong>TO DO [IMPORTANT]:</strong> Configure file storage for Sentry, and like everything else to be able to handle production</p>
<h2><a id="Up_and_Running_80"></a>Up and Running:</h2>
<ol>
<li>
<p>First set environment variable for Antenna and bucket:<br>
ANTENNA_ENV=&quot;/home/matthew.tung/antenna/dev.env&quot; (subject to change if you move everything)<br>
AWS_ACCESS_KEY_ID=&quot;**************YO5Q&quot;<br>
AWS_SECRET_ACCESS_KEY=&quot;**************xTdY&quot;<br>
(you can permanently set the last two with ‘aws configure’</p>
</li>
<li>
<p>cd into /antenna/ and start Antenna with: “./bin/run_web.sh”<br>
-if it throws and error you may have to: “sudo make build”</p>
</li>
<li>
<p>Antenna should now be running, periodically giving heartbeat messages</p>
</li>
<li>
<p>If you haven’t configured the server for ‘sudo systemctl start supervisord.service’, then in 3<br>
terminals source the virtualenv:</p>
<pre><code class="language-sh"><span class="hljs-built_in">source</span> /sentry_app/bin/activate
</code></pre>
<p>Then run:</p>
<pre><code>  sentry run cron
  sentry run worker
  sentry run web
</code></pre>
</li>
<li>
<p>Everything should be good to go now! For us go to &quot;<a href="https://brkpad.vivint.com/sentry/">https://brkpad.vivint.com/sentry/</a>&quot; to see!</p>
</li>
</ol>
<h2><a id="Random_Stuff_108"></a>Random Stuff:</h2>
<p>Wanna change how stuff looks and is sorted in the bucket?<br>
look at <code>/antenna/antenna/ext/s3/crashstorage.py</code> !</p>
<p>Wanna download or wipe everything from said bucket?<br>
<code>/sentry_breakpad/server/boto.py</code> has functions for that</p>
<p>Wanna change where dump files are stored in server before and after?<br>
Look at <code>boto.py</code> and <code>process_dump.py</code></p>
<p>Dealing with dump file meta data, not producing a processed stacktrace?<br>
Look at <code>process_dump.py</code></p>
<p>Stuff is going to Sentry, but it’s not in the right project?<br>
Look at <code>process_dump.py</code> and maybe <code>parse_for_sentry.py</code></p>
<p>Stuff is going to Sentry, but it’s showing the data how you like it?<br>
Look at <code>parse_for_sentry.py</code></p>
<p>Sentry starting to crash or not be able to handle all the reports?<br>
Look at config files in ‘/.sentry/’</p>
<p>In general, I think Sentry is a great tool to use for this purpose because it’s well-fleshed in terms of product and documentation and it is fairly versatile in how you can display reports. There is talk on the forums about sentry soon be able to support minidumps better, but right now, you’re stuck with <code>parse_for_sentry.py</code> :)</p>
