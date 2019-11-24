#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

gitOps Trial 
Update podman from git


"""

import sys
import os
import yaml
import git
import json 
import argparse
import subprocess



config_file = "config.yaml"

repo_dir = "repos"

podman_cmd = "./podman-sim"
parser = argparse.ArgumentParser()



parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
parser.add_argument("-f", "--config_file", default=config_file, help="Configuration yaml file")
parser.add_argument("-c", "--check", help="Run various checks", action="store_true")
parser.add_argument("-u", "--update", help="Update local repos", action="store_true")
parser.add_argument("-s", "--setup", help="Create local repos", action="store_true")
parser.add_argument("-d", "--destroy", help="Destroy local repos", action="store_true")
parser.add_argument("-a", "--apply", help="Apply configuration to local podman. Play or delete pods", action="store_true")

args = parser.parse_args()


vprint = print if args.verbose else lambda *a, **k: None



if args.config_file:
    config_file = args.config_file
    vprint("config_file =",  config_file )
    
    
if args.check:
    # Check if
    # - config file is correct (todo)
    # - git and podman canbe called
    # - base directory exists
    # - local repos and branch exists
    print("Not implemnted yet")
    
#
# Read the config file
#

# Try open the config file
try:
    stream = open(config_file, 'r')
except FileNotFoundError:
    print("File does not exists: ", config_file)   
    sys.exit()
except Exception as e: print(e)


# Load config file
config = yaml.load(stream, Loader=yaml.FullLoader)

if not(config):
    print("No config. Exiting")
    sys.exit()

# Check if there any repos defined
try:
    for r in config["repos"]: 
        try:
            vprint("Repo:", r["name"])
        except KeyError:
            print("Name missing in repo name in config file")

except KeyError:
    print("No repos in config file")
  

try:
    if len(config["repoDir"]) > 0:
        repo_dir = config["repoDir"]

except KeyError:
    vprint("No repoDir in config file")

vprint("Use repodir: ", repo_dir )

try:
    os.mkdir(repo_dir)
except FileExistsError:
    vprint("Repo dir exits: ", repo_dir )
  
        
        

#
# Assumption local branches exis    print("Update repos ...")ts remote and locally
# To-do: add checks
#

def git_commits_behind(repo, branch):
    repo = git.Repo(repo)
    origin = repo.remotes.origin
    origin.fetch()
    commits = list(repo.iter_commits(branch+'..origin/'+branch))
    return len(commits)

def git_pull(repo, branch):
    repo = git.Repo(repo)
    repo.remotes.origin.pull(branch)
    
    return 

def update_repos():
    print("Update repos ...")
    for r in config["repos"]: 
        try:
            vprint("Repo:", repo_dir+"/"+r["name"], " branch:", r["branch"])
        except KeyError:
            print("Name missing in repo name or branch in config file")
    
        s = git_commits_behind(repo_dir+"/"+r["name"], r["branch"])
        vprint("Pending commits " + r["branch"] + ":",  s )
        
        if s > 0:
            git_pull(repo_dir+"/"+r["name"], r["branch"])



#
# Update repos acording to configuration
#
if args.update:
    update_repos()
    # to-do; remove unneeded repos    


def get_pod_yaml_filenames(repo, branch, path):
    #
    # Get all yaml file names with 'kind: Pod' 
    #    
    pod_yamls = []
    for file in os.listdir(repo+"/"+path):
        if file.endswith(".yaml"):
            f = os.path.join(repo+"/"+path, file)
            with open(f) as yamlfile:
                if 'kind: Pod' in yamlfile.read():
                    print("- ", f)
                    pod_yamls.append(f)
    return pod_yamls
            

def get_podman_pods():
    #
    # Get the list of deployed pods in local podman
    #
    
    pods = subprocess.run([podman_cmd, 'pod', 'ps', '--format', '{{.ID}},{{.Name}}' ], stdout=subprocess.PIPE).stdout.decode('utf-8')
    
    pod_list = []
    for l in pods.split("\n"):
        if len(l) > 0:
            pod_list.append(l.split(","))
            
    return pod_list





def get_pod_yamls(repos):
    #
    # Get all pod yaml files with content and the filename into a list
    #    
    
    pod_yamls = []
    
    for r in repos: 
        try:
            rpath = repo_dir+"/"+r["name"]+"/"+r["path"]
            vprint("Repo and path:" , rpath)
        except KeyError:
            print("Name missing in repo name/path in config file")
            
    
        for file in os.listdir(rpath):
            if file.endswith(".yaml"):
                pod = {}
                f = os.path.join(rpath, file)
                pod['file'] = f
                stream = open(f, 'r')
                pod_yaml = yaml.load(stream, Loader=yaml.FullLoader)           
                
                try:
                    if pod_yaml['kind'] == 'Pod':
                        pod['yaml'] = pod_yaml
                        pod_yamls.append(pod)
                except KeyError:
                    continue
            
    return pod_yamls


#
# Setup local repos
#
if args.setup:
    vprint("Setup things ...")
    
    # Create repo dir
    try:
        os.mkdir(repo_dir)
    except FileExistsError:
        vprint("Repo dir exits: ", repo_dir )

    for r in config["repos"]: 
        try:
            vprint("Repo:", repo_dir+"/"+r["name"], " branch:", r["branch"])
        except KeyError:
            print("Name missing in repo name or branch in config file")
            
        if os.path.isdir(repo_dir+"/"+r["name"]+"/.git"):
            vprint("Repo exists:", repo_dir+"/"+r["name"] )
            git_pull(repo_dir+"/"+r["name"], r["branch"])
        else:
            vprint("Clone:", r["repoURL"], " to:", repo_dir+"/"+r["name"])
            repo = git.Repo.clone_from( r["repoURL"],
                repo_dir+"/"+r["name"],
                branch=r["branch"]
            )


#
# Apply configuration to local podman
#
if args.apply:
    vprint("Apply configuration to local podman ...")
    
    pod_yamls = []
    
    
    #
    # Deploy all pod yamls regardless if repo was updated or not
    #
    
    pod_yamls = get_pod_yamls(config["/"+"repos"])
    
    for p in pod_yamls:
        vprint("Run ...", [podman_cmd, 'play',  'kube',  p['file']])
        result = subprocess.run([podman_cmd, 'play',  'kube',  p['file']], stdout=subprocess.PIPE).stdout.decode('utf-8')
            # to-do: add error handling
        vprint("...", result)

            
    #
    # Remove unneeded pods: podman pod rm ID --force 
    #
        
    # Get the list of deployed pods in local podman
    pod_list = get_podman_pods()
    
    # print(pod_list)
    
    # Find pods in podman that are not ina any pod yaml
    for p in pod_list:
        found = False
        for y in pod_yamls:
            vprint("Podman: " + p[1] + "  Name in yaml: " + y["yaml"]["metadata"]["name"]  )
            if p[1] == y["yaml"]["metadata"]["name"]:
                found = True
        if not found:
            result = subprocess.run([podman_cmd, 'pod',  'rm',  p[0], '--force'], stdout=subprocess.PIPE).stdout.decode('utf-8')
            # to-do: add error handling
            vprint("...", result)              
        
